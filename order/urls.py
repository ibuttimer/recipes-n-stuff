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

from recipesnstuff import DEVELOPMENT
from .constants import (
    THIS_APP, ORDERS_URL, ORDERS_ROUTE_NAME,
    ORDER_SEARCH_URL, ORDER_SEARCH_ROUTE_NAME,
    ORDER_ID_URL, ORDER_ID_ROUTE_NAME,
    GENERATE_ORDER_PROD_URL, GENERATE_ORDER_PROD_ROUTE_NAME,
)
from .views import (
    OrderList, SearchOrderList, OrderDetail, generate_order_product,
)

# https://docs.djangoproject.com/en/4.1/topics/http/urls/#url-namespaces-and-included-urlconfs
app_name = THIS_APP

urlpatterns = [
    path(ORDERS_URL, OrderList.as_view(), name=ORDERS_ROUTE_NAME),
    path(ORDER_SEARCH_URL, SearchOrderList.as_view(),
         name=ORDER_SEARCH_ROUTE_NAME),
    path(ORDER_ID_URL, OrderDetail.as_view(), name=ORDER_ID_ROUTE_NAME),
]

if DEVELOPMENT:
    # add generate order product endpoint
    urlpatterns.extend([
        path(GENERATE_ORDER_PROD_URL, generate_order_product,
             name=GENERATE_ORDER_PROD_ROUTE_NAME),
    ])
