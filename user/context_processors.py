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
import re

from django.http import HttpRequest

from recipesnstuff.constants import (
    LOGIN_ROUTE_NAME, USER_MENU_CTX, SIGN_IN_MENU_CTX, REGISTER_MENU_CTX,
    REGISTER_ROUTE_NAME, IS_SUPER_CTX, ACCOUNTS_URL, LOGOUT_ROUTE_NAME,
    CHANGE_PASSWORD_ROUTE_NAME, AVATAR_URL_CTX
)
from recipesnstuff.settings import AVATAR_BLANK_URL
from utils import resolve_req, add_navbar_attr
from . import USER_ID_ROUTE_NAME
from .constants import USER_USERNAME_ROUTE_NAME
from .models import User
from .queries import get_social_providers


# regex to match socials; e.g. '/accounts/twitter/login/'
SOCIAL_REGEX = re.compile(
    rf'^/{ACCOUNTS_URL}(.*)/login/', re.IGNORECASE)


def _sign_in_route_check(request: HttpRequest, route: str):
    """ Check if sign in route """
    sign_in = route == LOGIN_ROUTE_NAME
    if not sign_in:
        # check socials
        match = SOCIAL_REGEX.match(request.path)
        if match:
            sign_in = match.group(1) in get_social_providers()

    return sign_in


def user_context(request: HttpRequest) -> dict:
    """
    Add user-specific context entries
    :param request: http request
    :return: dictionary to add to template context
    """
    context = {}
    called_by = resolve_req(request)
    if called_by:
        for ctx, check_func, is_dropdown_toggle in [
            (USER_MENU_CTX, lambda name: name in [
                USER_ID_ROUTE_NAME, USER_USERNAME_ROUTE_NAME,
                CHANGE_PASSWORD_ROUTE_NAME, LOGOUT_ROUTE_NAME
            ], True),
            (SIGN_IN_MENU_CTX,
             lambda name: _sign_in_route_check(request, name), False),
            (REGISTER_MENU_CTX,
             lambda name: name == REGISTER_ROUTE_NAME, False),
        ]:
            add_navbar_attr(
                context, ctx, is_active=check_func(called_by.url_name),
                is_dropdown_toggle=is_dropdown_toggle
            )

    context.update({
        IS_SUPER_CTX: request.user.is_superuser,
        AVATAR_URL_CTX:
            request.user.avatar.url if request.user.is_authenticated and
            User.AVATAR_BLANK not in request.user.avatar.url else
            AVATAR_BLANK_URL

        # IS_MODERATOR_CTX: is_moderator(request.user),
        # IS_AUTHOR_CTX: is_author(request.user),
    })
    return context
