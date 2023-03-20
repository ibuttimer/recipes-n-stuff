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

from recipes.constants import RECIPE_HOME_ROUTE_NAME
from recipesnstuff.constants import (
    HOME_MENU_CTX, HELP_MENU_CTX, HELP_ROUTE_NAME, HOME_ROUTE_NAME,
    APP_NAME, ABOUT_MENU_CTX, ABOUT_ROUTE_NAME, NO_ROBOTS_CTX
)
from recipesnstuff import VAL_TEST_PATH_PREFIX
from utils import resolve_req, add_navbar_attr

from .constants import APP_NAME_CTX, VAL_TEST_CTX, TOAST_POSITION_CTX
from .views import ToastPosition


def base_context(request: HttpRequest) -> dict:
    """
    Add base-specific context entries
    :param request: http request
    :return: dictionary to add to template context
    """
    context = {
        APP_NAME_CTX: APP_NAME,
        VAL_TEST_CTX: request.path.find(VAL_TEST_PATH_PREFIX) >= 0
    }
    no_robots = False
    called_by = resolve_req(request)
    if called_by:
        for ctx, routes in [
            (HOME_MENU_CTX, [
                HOME_ROUTE_NAME, RECIPE_HOME_ROUTE_NAME
            ]),
            (HELP_MENU_CTX, [HELP_ROUTE_NAME]),
            (ABOUT_MENU_CTX, [ABOUT_ROUTE_NAME]),
        ]:
            add_navbar_attr(
                context, ctx, is_active=called_by.url_name in routes)

        # set no robots
        # allauth route names start with 'account_' and have no app name
        no_robots = called_by.app_name == '' and \
            called_by.url_name.startswith('account_')
        # admin routes have app name 'admin'
        no_robots = no_robots or called_by.app_name == 'admin'

    context.update({
        NO_ROBOTS_CTX: no_robots,
        TOAST_POSITION_CTX: ToastPosition.DEFAULT.value
    })

    return context
