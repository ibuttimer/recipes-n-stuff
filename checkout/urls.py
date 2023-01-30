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
    CHECKOUT_PAID_URL, CHECKOUT_PAID_ROUTE_NAME
)
from .views import (
    checkout, create_payment_intent, payment_complete
)

# https://docs.djangoproject.com/en/4.1/topics/http/urls/#url-namespaces-and-included-urlconfs
app_name = THIS_APP

urlpatterns = [
    path(CHECKOUT_PAY_URL, checkout, name=CHECKOUT_PAY_ROUTE_NAME),
    path(CHECKOUT_CREATE_PAYMENT_URL, create_payment_intent,
         name=CHECKOUT_CREATE_PAYMENT_ROUTE_NAME),
    path(CHECKOUT_PAID_URL, payment_complete, name=CHECKOUT_PAID_ROUTE_NAME),
]
