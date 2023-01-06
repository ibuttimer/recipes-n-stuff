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

from recipesnstuff import PROFILES_APP_NAME

from .constants import (
    ADDRESSES_URL, ADDRESSES_ROUTE_NAME,
    ADDRESS_NEW_URL, ADDRESS_NEW_ROUTE_NAME,
    COUNTRYINFO_CODE_URL, COUNTRYINFO_CODE_ROUTE_NAME
)
from .views import AddressCreate, AddressList, subdivision_name

# https://docs.djangoproject.com/en/4.1/topics/http/urls/#url-namespaces-and-included-urlconfs
app_name = PROFILES_APP_NAME

urlpatterns = [
    path(ADDRESSES_URL, AddressList.as_view(), name=ADDRESSES_ROUTE_NAME),
    path(ADDRESS_NEW_URL, AddressCreate.as_view(),
         name=ADDRESS_NEW_ROUTE_NAME),
    # path(ADDRESS_ID_URL, views.UserDetailById.as_view(),
    #      name=ADDRESS_ID_ROUTE_NAME),
    # path(ADDRESSES_BY_USER_ID_URL, views.UserDetailByUsername.as_view(),
    #      name=ADDRESSES_BY_USER_ID_ROUTE_NAME),

    path(COUNTRYINFO_CODE_URL, subdivision_name,
         name=COUNTRYINFO_CODE_ROUTE_NAME),
]
