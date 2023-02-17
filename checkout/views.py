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
from http import HTTPStatus

import stripe
from django.contrib.auth.decorators import login_required
from django.core.exceptions import BadRequest
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.views.decorators.http import require_http_methods

from base.views import info_toast_payload, InfoModalTemplate
from order.persist import save_order
from recipesnstuff import HOME_ROUTE_NAME
from recipesnstuff.settings import (
    STRIPE_PUBLISHABLE_KEY, STRIPE_SECRET_KEY
)
from subscription.forms import get_currency_choices
from subscription.middleware import subscription_payment_completed
from utils import (
    GET, POST, PATCH, namespaced_url, app_template_path,
    replace_inner_html_payload, TITLE_CTX, PAGE_HEADING_CTX, DELETE,
    rewrite_payload, entity_delete_result_payload, reverse_q, redirect_payload
)
from .basket import Basket, navbar_basket_html

from .constants import (
    THIS_APP, STRIPE_PUBLISHABLE_KEY_CTX, STRIPE_RETURN_URL_CTX,
    CHECKOUT_PAID_ROUTE_NAME, BASKET_SES, BASKET_CTX, CURRENCIES_CTX,
    BASKET_CCY_QUERY, ITEM_QUERY, UNITS_QUERY, ORDER_NUM_CTX
)
from .currency import is_valid_code

# set Stripe API key
stripe.api_key = STRIPE_SECRET_KEY


def get_basket(request: HttpRequest) -> Basket:
    """
    Get the session basket.
    :param request: http request
    :return: basket
    """
    if BASKET_SES not in request.session:
        raise BadRequest('Basket not found')

    return Basket.from_jsonable(
        request.session[BASKET_SES])


def set_basket(request: HttpRequest, basket: Basket) -> Basket:
    """
    Set the session basket.
    :param request: http request
    :param basket: current basket
    :return: basket
    """
    request.session[BASKET_SES] = basket


@login_required
@require_http_methods([GET])
def checkout(request: HttpRequest) -> HttpResponse:
    """
    View function to display checkout.
    :param request: http request
    :return: response
    """
    basket = get_basket(request)

    title = "Checkout"

    context = {
        TITLE_CTX: title,
        PAGE_HEADING_CTX: title,
        STRIPE_PUBLISHABLE_KEY_CTX: STRIPE_PUBLISHABLE_KEY,
        STRIPE_RETURN_URL_CTX: namespaced_url(
            THIS_APP, CHECKOUT_PAID_ROUTE_NAME
        )
    }
    context.update(
        basket_context(basket)
    )

    return render(request, app_template_path(
        THIS_APP, 'checkout.html'
    ), context=context)


def basket_context(basket: Basket) -> dict:
    """
    Get context for basket template
    :param basket: current basket
    :return: context
    """
    return {
        BASKET_CTX: basket,
        CURRENCIES_CTX: get_currency_choices()
    }


@login_required
@require_http_methods([POST])
def create_payment_intent(request: HttpRequest) -> HttpResponse:
    """
    View function to create a Stripe PaymentIntent
    :param request: http request
    :return: response
    """
    basket = get_basket(request)

    # Create a PaymentIntent with the order amount and currency
    intent = stripe.PaymentIntent.create(
        amount=basket.payment_total,
        currency=basket.currency,
        automatic_payment_methods={
            'enabled': False,
        },
    )
    return JsonResponse({
        'clientSecret': intent['client_secret']
    }, status=HTTPStatus.OK)


@login_required
@require_http_methods([PATCH, DELETE])
def update_basket(request: HttpRequest) -> HttpResponse:
    """
    Update the basket
    :param request: http request
    :return: response
    """
    basket = get_basket(request)

    redraw_basket = False
    redraw_msg = False
    if request.method == PATCH and BASKET_CCY_QUERY in request.GET:
        # change currency
        new_ccy = request.GET[BASKET_CCY_QUERY]
        if is_valid_code(new_ccy):
            basket.currency = new_ccy
            redraw_basket = True
    elif ITEM_QUERY in request.GET:
        # add/remove item from basket
        item = int(request.GET[ITEM_QUERY])
        if request.method == DELETE:
            # remove item
            redraw_basket = basket.remove(item)
            if redraw_basket:
                redraw_msg = entity_delete_result_payload(
                    "#id--item-deleted-modal-body", True, 'item')

        elif request.method == PATCH and UNITS_QUERY in request.GET:
            # change num of units of item
            units = int(request.GET[UNITS_QUERY])
            redraw_basket = basket.update_item_units(item, units)

    if redraw_basket or redraw_msg:
        # need to update serialised basket in request
        basket.add_to_request(request)

        if redraw_basket:
            redraw_basket = redraw_basket_payload(basket)
        payload = rewrite_payload(
            redraw_basket or None, redraw_msg or None
        )
    else:
        payload = {}

    return JsonResponse(
        payload, status=HTTPStatus.OK if payload else HTTPStatus.BAD_REQUEST)


def redraw_basket_payload(basket: Basket) -> dict:
    """
    Generate basket redraw payload
    :param basket: basket to redraw
    :return: payload
    """
    return rewrite_payload(
        # redraw on screen basket
        replace_inner_html_payload(
            "#id__basket-div", render_to_string(
                app_template_path(
                    THIS_APP, "snippet", "basket.html"),
                context=basket_context(basket))
        ),
        # redraw navbar basket icon
        navbar_basket_html(basket)
    )


@login_required
@require_http_methods([DELETE])
def clear_basket(request: HttpRequest) -> HttpResponse:
    """
    Clear the basket
    :param request: http request
    :return: response
    """
    basket = get_basket(request)

    basket.close(request=request)

    payload = redirect_payload(reverse_q(HOME_ROUTE_NAME), pause=2000)
    payload.update(
        info_toast_payload(InfoModalTemplate(app_template_path(
            THIS_APP, "messages", "basket_cleared.html")))
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
    basket = get_basket(request)
    save_order(basket)

    basket.close(request=request)

    subscription_payment_completed(request)

    return render(request, app_template_path(
        THIS_APP, 'payment_complete.html'
    ), context={
        TITLE_CTX: "Payment complete",
        PAGE_HEADING_CTX: "Payment received",
        ORDER_NUM_CTX: basket.order_num
    })
