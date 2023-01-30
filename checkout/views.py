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
from django.views.decorators.http import require_http_methods

from recipesnstuff.settings import (
    DEFAULT_CURRENCY, STRIPE_PUBLISHABLE_KEY, STRIPE_SECRET_KEY
)
from utils import GET, namespaced_url, app_template_path, POST

from .constants import (
    THIS_APP, STRIPE_PUBLISHABLE_KEY_CTX, STRIPE_RETURN_URL_CTX,
    PAYMENT_AMOUNT_SES, PAYMENT_CURRENCY_SES, ZERO_DECIMAL_CURRENCIES,
    THREE_DECIMAL_CURRENCIES, CHECKOUT_PAID_ROUTE_NAME
)


# set Stripe API key
stripe.api_key = STRIPE_SECRET_KEY


@login_required
@require_http_methods([GET])
def checkout(request: HttpRequest) -> HttpResponse:
    """
    View function to display checkout.
    :param request: http request
    :return: response
    """
    return render(request, app_template_path(
        THIS_APP, 'checkout.html'
    ), context={
        STRIPE_PUBLISHABLE_KEY_CTX: STRIPE_PUBLISHABLE_KEY,
        STRIPE_RETURN_URL_CTX: namespaced_url(
            THIS_APP, CHECKOUT_PAID_ROUTE_NAME
        )
    })


@login_required
@require_http_methods([POST])
def create_payment_intent(request: HttpRequest) -> HttpResponse:
    """
    View function to create a Stripe PaymentIntent
    :param request: http request
    :return: response
    """

    if PAYMENT_AMOUNT_SES not in request.session or \
            PAYMENT_CURRENCY_SES not in request.session:
        raise BadRequest('Invalid payment amount')

    # amount must be how much to charge in the smallest currency unit
    currency = request.session[PAYMENT_CURRENCY_SES]
    factor = 0 if currency in ZERO_DECIMAL_CURRENCIES else \
        3 if currency in THREE_DECIMAL_CURRENCIES else 2
    amount = int(request.session[PAYMENT_AMOUNT_SES] * 10**factor)
    if factor == 3:
        # must round amounts to the nearest ten
        amount = round(amount/10, 1) * 10

    # Create a PaymentIntent with the order amount and currency
    intent = stripe.PaymentIntent.create(
        amount=amount,
        currency=currency,
        automatic_payment_methods={
            'enabled': True,
        },
    )
    return JsonResponse({
        'clientSecret': intent['client_secret']
    }, status=HTTPStatus.OK)


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
