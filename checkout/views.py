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

from recipesnstuff.settings import (
    DEFAULT_CURRENCY, STRIPE_PUBLISHABLE_KEY, STRIPE_SECRET_KEY
)
from subscription.forms import get_currency_choices
from utils import (
    GET, POST, PATCH, namespaced_url, app_template_path,
    replace_inner_html_payload
)
from .basket import Basket

from .constants import (
    THIS_APP, STRIPE_PUBLISHABLE_KEY_CTX, STRIPE_RETURN_URL_CTX,
    CHECKOUT_PAID_ROUTE_NAME, BASKET_SES, BASKET_CTX, CURRENCIES_CTX,
    BASKET_CCY_QUERY
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


@login_required
@require_http_methods([GET])
def checkout(request: HttpRequest) -> HttpResponse:
    """
    View function to display checkout.
    :param request: http request
    :return: response
    """
    basket = get_basket(request)

    context = {
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
@require_http_methods([PATCH])
def update_basket(request: HttpRequest) -> HttpResponse:
    """
    Update the basket
    :param request: http request
    :return: response
    """

    basket = get_basket(request)

    success = False
    if BASKET_CCY_QUERY in request.GET:
        new_ccy = request.GET[BASKET_CCY_QUERY]
        if is_valid_code(new_ccy):
            basket.currency = new_ccy
            success = True

    payload = None if not success else replace_inner_html_payload(
        "#id__basket-div", render_to_string(
            app_template_path(
                THIS_APP, "snippet", "basket.html"),
            context=basket_context(basket))
    )

    return JsonResponse(
        payload, status=HTTPStatus.OK if success else HTTPStatus.BAD_REQUEST)


@login_required
@require_http_methods([GET])
def payment_complete(request: HttpRequest) -> HttpResponse:
    """
    View function to display payment result.
    :param request: http request
    :return: response
    """
    return render(request, app_template_path(
        THIS_APP, 'payment_complete.html'
    ), context={
    })
