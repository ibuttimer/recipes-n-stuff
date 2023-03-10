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
#

from django.urls import path

from .constants import (
    THIS_APP,
    CHECKOUT_PAY_URL, CHECKOUT_PAY_ROUTE_NAME,
    CHECKOUT_CREATE_PAYMENT_URL, CHECKOUT_CREATE_PAYMENT_ROUTE_NAME,
    CHECKOUT_UPDATE_BASKET_URL, CHECKOUT_UPDATE_BASKET_ROUTE_NAME,
    CHECKOUT_ADDRESS_URL, CHECKOUT_ADDRESS_ROUTE_NAME,
    CHECKOUT_CLEAR_URL, CHECKOUT_CLEAR_ROUTE_NAME,
    CHECKOUT_PAID_URL, CHECKOUT_PAID_ROUTE_NAME,
    CHECKOUT_STRIPE_WEBHOOK_URL, CHECKOUT_STRIPE_WEBHOOK_ROUTE_NAME,
    CHECKOUT_REORDER_URL, CHECKOUT_REORDER_ROUTE_NAME
)
from .views import (
    checkout, create_payment_intent, payment_complete, update_basket,
    set_address, clear_basket, reorder
)
from .webhooks import stripe_webhook


# https://docs.djangoproject.com/en/4.1/topics/http/urls/#url-namespaces-and-included-urlconfs
app_name = THIS_APP

urlpatterns = [
    path(CHECKOUT_PAY_URL, checkout, name=CHECKOUT_PAY_ROUTE_NAME),
    path(CHECKOUT_CREATE_PAYMENT_URL, create_payment_intent,
         name=CHECKOUT_CREATE_PAYMENT_ROUTE_NAME),
    path(CHECKOUT_UPDATE_BASKET_URL, update_basket,
         name=CHECKOUT_UPDATE_BASKET_ROUTE_NAME),
    path(CHECKOUT_ADDRESS_URL, set_address, name=CHECKOUT_ADDRESS_ROUTE_NAME),
    path(CHECKOUT_REORDER_URL, reorder, name=CHECKOUT_REORDER_ROUTE_NAME),
    path(CHECKOUT_CLEAR_URL, clear_basket,
         name=CHECKOUT_CLEAR_ROUTE_NAME),
    path(CHECKOUT_PAID_URL, payment_complete, name=CHECKOUT_PAID_ROUTE_NAME),
    path(CHECKOUT_STRIPE_WEBHOOK_URL, stripe_webhook,
         name=CHECKOUT_STRIPE_WEBHOOK_ROUTE_NAME),
]
