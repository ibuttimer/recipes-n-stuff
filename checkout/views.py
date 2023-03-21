#  MIT License
#
#  Copyright (c) 2023 Ian Buttimer
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to
#  deal in the Software without restriction, including without limitation the
#  rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
#  sell copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#  FROM,OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#  DEALINGS IN THE SOFTWARE.
import json
from collections import namedtuple
from http import HTTPStatus

import stripe
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.views.decorators.http import require_http_methods
from more_itertools import one

from base.views import info_toast_payload, ToastTemplate
from order.misc import decode_sku
from order.models import ProductType, OrderStatus
from order.persist import save_order
from order.queries import get_delivery_product
from order.views.dto import OrderIdsBundle
from order.views.utils import order_permission_check
from profiles.constants import ADDRESSES_ROUTE_NAME
from profiles.dto import AddressDto
from profiles.templatetags.address_element_id import address_element_id
from profiles.views.address_by import get_address
from profiles.views.address_queries import addresses_query
from recipesnstuff import HOME_ROUTE_NAME, PROFILES_APP_NAME
from recipesnstuff.settings import STRIPE_PUBLISHABLE_KEY
from subscription.constants import USER_SUB_ID_SES
from subscription.forms import get_currency_choices
from subscription.middleware import subscription_payment_completed
from subscription.models import FeatureType
from subscription.views.dto import SubscriptionFeatureDto
from subscription.subscription_queries import user_subscription_features
from utils import (
    GET, POST, PATCH, namespaced_url, app_template_path,
    replace_inner_html_payload, TITLE_CTX, PAGE_HEADING_CTX, DELETE,
    rewrite_payload, entity_delete_result_payload, reverse_q,
    redirect_payload, replace_html_payload, Crud, USER_QUERY
)
from .basket import (
    Basket, navbar_basket_html, get_session_basket,
    add_ingredient_box_to_basket
)

from .constants import (
    THIS_APP, STRIPE_PUBLISHABLE_KEY_CTX, STRIPE_RETURN_URL_CTX,
    CHECKOUT_PAID_ROUTE_NAME, BASKET_CTX, CURRENCIES_CTX, BASKET_CCY_QUERY,
    ITEM_QUERY, UNITS_QUERY, ORDER_NUM_CTX, ADDRESS_LIST_CTX, ADDRESS_DTO_CTX,
    CONTENT_FORMAT_CTX, DELIVERY_LIST_CTX, DELIVERY_QUERY, DELIVERY_REQ_CTX,
    CHECKOUT_PAY_ROUTE_NAME
)
from .currency import is_valid_code
from .dto import DeliveryDto
from .on_complete import get_on_complete
import checkout.stripe_cfg
from checkout.stripe_cfg import generate_payment_intent_data


# (display text, FeatureType choice)
FreeDelivery = namedtuple('FreeDelivery', ['display', 'feature_type'],
                          defaults=[None, None])


@login_required
@require_http_methods([GET])
def checkout(request: HttpRequest) -> HttpResponse:
    """
    View function to display checkout.
    :param request: http request
    :return: response
    """
    order_permission_check(request, Crud.READ)

    basket, _ = get_session_basket(request)
    get_on_complete(request)

    title = "Checkout"

    addresses = [
        AddressDto.from_model(address, is_selected=address == basket.address)
        for address in addresses_query(user=request.user)
    ]
    if len(addresses) == 0:
        messages.add_message(
            request, messages.INFO, 'Please add an address before checkout.')
        response = redirect(
            reverse_q(
                namespaced_url(PROFILES_APP_NAME, ADDRESSES_ROUTE_NAME),
                query_kwargs={
                    USER_QUERY: request.user.username
                }
            )
        )
    else:
        # set address to user default if not set
        basket.set_address_as_default(force=False)

        context = {
            TITLE_CTX: title,
            PAGE_HEADING_CTX: title,
            STRIPE_PUBLISHABLE_KEY_CTX: STRIPE_PUBLISHABLE_KEY,
            STRIPE_RETURN_URL_CTX: namespaced_url(
                THIS_APP, CHECKOUT_PAID_ROUTE_NAME
            ),
            ADDRESS_LIST_CTX: addresses
        }
        basket_context(basket, context=context)
        delivery_context(basket, context=context)

        response = render(request, app_template_path(
            THIS_APP, 'checkout.html'
        ), context=context)

    return response


def basket_context(basket: Basket, context: dict = None) -> dict:
    """
    Get context for basket template
    :param basket: current basket
    :param context: context to update
    :return: context
    """
    if context is None:
        context = {}
    context.update({
        BASKET_CTX: basket,
        CURRENCIES_CTX: get_currency_choices()
    })
    return context


def delivery_context(basket: Basket, context: dict = None,
                     is_update: bool = False) -> dict:
    """
    Context for delivery
    :param basket: current basket
    :param context: context to update; default create new
    :param is_update: is a basket update; default False
    :return: context
    """
    if context is None:
        context = {}

    # no delivery if only subscription in basket
    no_delivery = sum(
        map(lambda item: decode_sku(
            item.sku).prod_type.is_subscription_option, basket.items)
    ) == len(basket.items)

    context.update({
        BASKET_CTX: basket,
        DELIVERY_REQ_CTX: not no_delivery,
    })

    if not no_delivery:
        # check user's subscription for a free delivery option
        free_delivery: FreeDelivery = None
        sub_features, sub_start = user_subscription_features(basket.user)
        if sub_features:
            # list of free delivery FeatureType choice values
            free_delivery_feat = list(map(
                lambda feat: feat.choice, FeatureType.free_delivery()
            ))
            # list of free delivery SubscriptionFeature in user's subscription
            free_delivery_feat = list(filter(
                lambda feat: feat.feature_type in free_delivery_feat,
                sub_features    # list of user's subscription features
            ))
            # list of free delivery SubscriptionFeatureDto
            free_delivery_feat = list(
                map(SubscriptionFeatureDto.from_model, free_delivery_feat)
            )
            # check each free delivery feature to see if order qualifies
            for feature in free_delivery_feat:
                qualifies, remaining_x_free = feature.order_qualifies(
                    basket.user, basket.subtotal_base_ccy)
                if qualifies:
                    free_delivery = \
                        FreeDelivery(display=f'{feature.display_text} '
                                             f'[{remaining_x_free} remaining]',
                                     feature_type=feature.feature_type)
                    break

        delivery_prods = get_delivery_product(basket.address.country)
        if free_delivery:
            if not is_update:
                # set free delivery as default
                delivery_prods = list(delivery_prods)
                basket.delivery = one(filter(
                    lambda del_opt:
                    ProductType.FREE_DELIVERY.is_from_choice(del_opt.type),
                    delivery_prods
                ))
                basket.feature_type = free_delivery.feature_type
        else:
            # remove free delivery option
            delivery_prods = list(filter(
                lambda del_opt:
                not ProductType.FREE_DELIVERY.is_from_choice(del_opt.type),
                delivery_prods
            ))

        def detail_feature_type(delivery):
            """ Get args for DeliveryDto """
            detail = free_delivery if ProductType.FREE_DELIVERY.is_from_choice(
                delivery.type) else FreeDelivery()
            return {
                'detail': detail.display,
                'feature_type': detail.feature_type,
            }

        delivery_list = None if basket.address is None else [
            DeliveryDto.from_model(
                delivery, basket, is_selected=delivery == basket.delivery,
                **detail_feature_type(delivery)
            ) for delivery in delivery_prods
        ]
        context.update({
            DELIVERY_LIST_CTX: delivery_list
        })

    return context


def delivery_payload(basket: Basket, is_update: bool = False) -> dict:
    """
    Redraw payload for delivery
    :param basket: current basket
    :param is_update: is a basket update; default False
    :return: payload
    """
    return replace_inner_html_payload(
        "#id__del-div", render_to_string(
            app_template_path(
                THIS_APP, "snippet", "delivery_options.html"),
            context=delivery_context(basket, is_update=is_update))
    )


@login_required
@require_http_methods([POST])
def create_payment_intent(request: HttpRequest) -> HttpResponse:
    """
    View function to create a Stripe PaymentIntent
    :param request: http request
    :return: response
    """
    order_permission_check(request, Crud.CREATE)

    basket, _ = get_session_basket(request)
    # set address to user default if not set
    basket.set_address_as_default(force=False)

    save_order(basket, status=OrderStatus.PENDING_PAYMENT)

    # Create a PaymentIntent with the order amount and currency
    # https://stripe.com/docs/api/payment_intents/create
    intent = stripe.PaymentIntent.create(
        amount=basket.payment_total,
        currency=basket.currency,
        automatic_payment_methods={
            'enabled': False,
        },
        **generate_payment_intent_data(basket, request)
    )
    return JsonResponse({
        'clientSecret': intent['client_secret']
    }, status=HTTPStatus.OK)


@login_required
@require_http_methods([PATCH, DELETE])
def update_basket(request: HttpRequest) -> HttpResponse:
    """
    Update the basket; currency, remove item or change quantity
    :param request: http request
    :return: response
    """
    order_permission_check(request, Crud.UPDATE)

    basket, _ = get_session_basket(request)

    payload = {}
    redraw_basket = False
    redraw_delivery = False
    redraw_msg = False
    if request.method == PATCH and BASKET_CCY_QUERY in request.GET:
        # change currency
        new_ccy = request.GET[BASKET_CCY_QUERY]
        if is_valid_code(new_ccy):
            basket.currency = new_ccy
            redraw_basket = True
    elif request.method == PATCH and DELIVERY_QUERY in request.GET:
        # change delivery
        # request param in form '<delivery prod id>-<FeatureType choice>'
        splits = request.GET[DELIVERY_QUERY].split('-')
        basket.delivery = int(splits[0])
        basket.feature_type = splits[1] if len(splits) > 1 else None
        redraw_delivery = True
    elif ITEM_QUERY in request.GET:
        # add/remove item from basket
        item = int(request.GET[ITEM_QUERY])
        if request.method == DELETE:
            if basket.num_products == 1:
                # clear basket as only 1 product left
                payload = action_clear_basket(request)
            else:
                # remove item
                redraw_basket = basket.remove(item)
                if redraw_basket:
                    redraw_msg = entity_delete_result_payload(
                        "#id--item-deleted-modal-body", True, 'item')

        elif request.method == PATCH and UNITS_QUERY in request.GET:
            # change num of units of item
            units = int(request.GET[UNITS_QUERY])
            redraw_basket = basket.update_item_units(item, units)

    if redraw_basket or redraw_delivery or redraw_msg:
        # need to update serialised basket in request
        basket.add_to_request(request)

        if redraw_basket:
            redraw_basket = basket_payload(basket, is_update=True)
        if redraw_delivery:
            redraw_delivery = delivery_payload(basket, is_update=True)
        payload = rewrite_payload(
            redraw_basket or None, redraw_delivery or None, redraw_msg or None
        )

    return payload if isinstance(payload, HttpResponse) else JsonResponse(
        payload, status=HTTPStatus.OK if payload else HTTPStatus.BAD_REQUEST)


def basket_payload(basket: Basket, is_update: bool = False) -> dict:
    """
    Generate basket redraw payload
    :param basket: basket to redraw
    :param is_update: is a basket update; default False
    :return: payload
    """
    return rewrite_payload(
        # redraw on screen basket
        replace_inner_html_payload(
            "#id__div-basket", render_to_string(
                app_template_path(
                    THIS_APP, "snippet", "basket.html"),
                context=basket_context(basket))
        ),
        # redraw navbar basket icon
        navbar_basket_html(basket),
        # redraw delivery
        delivery_payload(basket, is_update=is_update),
    )


@login_required
@require_http_methods([PATCH])
def set_address(request: HttpRequest, pk: int) -> HttpResponse:
    """
    Set the delivery address
    :param request: http request
    :param pk: id of address to set
    :return: response
    """
    order_permission_check(request, Crud.UPDATE)

    basket, _ = get_session_basket(request)

    old_address = basket.address
    new_address, _ = get_address(pk)
    basket.address = new_address
    # need to update serialised basket in request
    basket.add_to_request(request)

    addresses = [
        AddressDto.from_model(address, is_selected=address == basket.address)
        for address in [old_address, new_address]
    ]

    # redraw changed addresses
    payload = [
        replace_html_payload(
            f"#{address_element_id(address_dto, 'div')}", render_to_string(
                app_template_path(
                    PROFILES_APP_NAME, "address_dto.html"),
                context={
                    ADDRESS_DTO_CTX: address_dto,
                    CONTENT_FORMAT_CTX: 'select'
                }
            )
        ) for address_dto in addresses
    ]
    # redraw delivery; address has changed so don't treat as update
    payload.append(delivery_payload(basket, is_update=False))

    payload = rewrite_payload(*payload)

    return JsonResponse(payload, status=HTTPStatus.OK)


@login_required
@require_http_methods([DELETE])
def clear_basket(request: HttpRequest) -> HttpResponse:
    """
    Clear the basket
    :param request: http request
    :return: response
    """
    order_permission_check(request, Crud.UPDATE)

    return action_clear_basket(request)


def action_clear_basket(request: HttpRequest) -> HttpResponse:
    """
    Clear the basket
    :param request: http request
    :return: response
    """
    basket, _ = get_session_basket(request)
    on_complete, _ = get_on_complete(request)

    basket.close(request=request)
    on_complete.close(request=request)

    payload = redirect_payload(reverse_q(HOME_ROUTE_NAME), pause=2000)
    payload.update(
        info_toast_payload(ToastTemplate(
            template=app_template_path(
                THIS_APP, "messages", "basket_cleared.html"))
        )
    )

    return JsonResponse(
        payload, status=HTTPStatus.OK if payload else HTTPStatus.BAD_REQUEST)


@login_required
@require_http_methods([GET])
def payment_complete(request: HttpRequest) -> HttpResponse:
    """
    View function to display payment result.
    :param request: http request
    :return: response
    """
    order_permission_check(request, Crud.UPDATE)

    basket, _ = get_session_basket(request)
    on_complete, _ = get_on_complete(request)
    on_complete.execute()

    basket.close(request=request)
    on_complete.close(request=request)

    if USER_SUB_ID_SES in request.session:
        subscription_payment_completed(request)

    return render(request, app_template_path(
        THIS_APP, 'payment_complete.html'
    ), context={
        TITLE_CTX: "Payment complete",
        PAGE_HEADING_CTX: "Payment received",
        ORDER_NUM_CTX: basket.order_num
    })


@login_required
@require_http_methods([GET])
def reorder(request: HttpRequest, pk: int) -> HttpResponse:
    """
    Reorder a previous order
    :param request: http request
    :param pk: id of order to repeat
    :return: response
    """
    order_permission_check(request, Crud.CREATE)

    order = OrderIdsBundle.from_id(pk)

    basket, _ = get_session_basket(request)

    for item in order.items:
        if item.prod_type.is_ingredient_box_option:
            add_ingredient_box_to_basket(
                request, item.type_id, count=item.quantity,
                basket=basket)
        # else ignore other types

    # need to update serialised basket in request
    basket.add_to_request(request)

    return redirect(
        namespaced_url(THIS_APP, CHECKOUT_PAY_ROUTE_NAME)
    )
