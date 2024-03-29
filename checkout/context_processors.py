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

from django.http import HttpRequest

from recipesnstuff.constants import NO_ROBOTS_CTX
from utils import resolve_req
from .basket import get_session_basket, navbar_basket_context
from .constants import THIS_APP
from .urls import urlpatterns


route_names = list(map(lambda route: route.name, urlpatterns))


def checkout_context(request: HttpRequest) -> dict:
    """
    Add base-specific context entries
    :param request: http request
    :return: dictionary to add to template context
    """
    basket, _ = get_session_basket(request)
    context = navbar_basket_context(basket)

    no_robots = False
    called_by = resolve_req(request)
    if called_by:
        no_robots = called_by.app_name == THIS_APP and \
            called_by.url_name in route_names

    if no_robots:
        # no robots in checkout app urls
        context.update({
            NO_ROBOTS_CTX: True
        })

    return context
