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
from datetime import datetime, timezone
from enum import Enum, auto
from typing import TypeVar, Callable

from django.http import HttpRequest
from django.shortcuts import redirect
from django.contrib import messages
import json_fix

from recipesnstuff.constants import LOGOUT_ROUTE_NAME
from recipesnstuff.settings import STATIC_URL
from subscription.views.subscription_queries import user_has_subscription
from utils import namespaced_url, resolve_req

from .constants import (
    THIS_APP, SUBSCRIPTION_CHOICE_ROUTE_NAME, SUBSCRIPTION_PICK_ROUTE_NAME
)

SUB_EXPIRY = 'sub_expiry'   # subscription expiry date
SUB_STATUS = 'sub_status'   # subscription status


# workaround for self type hints from https://peps.python.org/pep-0673/
TypeSubscriptionStatus = \
    TypeVar("TypeSubscriptionStatus", bound="SubscriptionStatus")


class SubscriptionStatus(Enum):
    """ Enum represent subscription status """
    NOT_FOUND = auto()
    EXPIRED = auto()
    WIP = auto()
    VALID = auto()
    IGNORE = auto()     # anonymous user

    @staticmethod
    def from_jsonable(jsonable: dict) -> TypeSubscriptionStatus:
        """
        Convert json representation to enum
        :param jsonable: json representation
        :return: SubscriptionStatus if found otherwise original argument
        """
        status = jsonable
        if isinstance(jsonable, dict):
            if jsonable.get('type', None) == SubscriptionStatus.__name__:
                value = jsonable.get('value', None)
                for sub_status in SubscriptionStatus:
                    if sub_status.value == value:
                        status = sub_status
                        break
        return status

    def __json__(self):
        # return a built-in object that is naturally jsonable
        return {
            'type': SubscriptionStatus.__name__,
            'value': self.value
        }


PROCESS_NORMALLY = [
    SubscriptionStatus.VALID, SubscriptionStatus.WIP,
    SubscriptionStatus.IGNORE
]
SUB_CHOICE_ROUTE = namespaced_url(THIS_APP, SUBSCRIPTION_CHOICE_ROUTE_NAME)
NO_SUB_SANDBOX = [
    # no subscription restricted to choose subscription or logout
    SUB_CHOICE_ROUTE, LOGOUT_ROUTE_NAME,
    namespaced_url(THIS_APP, SUBSCRIPTION_PICK_ROUTE_NAME)
]


class SubscriptionMiddleware:
    """
    A middleware factory to check user subscription status
    https://docs.djangoproject.com/en/4.1/topics/http/middleware/
    https://docs.djangoproject.com/en/4.1/topics/http/sessions/
    """
    def __init__(self, get_response: Callable):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request: HttpRequest) -> Callable:
        """
        Code to be executed for each request before the view
        (and later middleware) are called.
        :param request:
        :return: callable for next step in middleware chain
        """
        msg = None
        expiry = None       # subscription expiry date
        sandbox = False     # stay in subscription sandbox flag
        status = SubscriptionStatus.IGNORE if request.user.is_superuser else \
            request.session.get(SUB_STATUS, SubscriptionStatus.NOT_FOUND) \
            if request.user.is_authenticated else SubscriptionStatus.IGNORE
        status = SubscriptionStatus.from_jsonable(status)

        if status == SubscriptionStatus.VALID:
            # check expiry date
            expiry = datetime.fromtimestamp(
                request.session[SUB_EXPIRY], tz=timezone.utc)
            if expiry < datetime.now(tz=timezone.utc):
                status = SubscriptionStatus.EXPIRED
                msg = self.sub_expired_msg(expiry)
        elif status in [SubscriptionStatus.WIP, SubscriptionStatus.EXPIRED]:
            # check request url ok
            called_by = resolve_req(request)
            req_route = None if not called_by else \
                namespaced_url(called_by.namespace, called_by.url_name)
            sandbox = req_route not in NO_SUB_SANDBOX
            if sandbox and called_by:
                # check if req was for static asset and allow if so
                # e.g. android-chrome-192x192.png
                doc_root = called_by.kwargs.get('document_root', None)
                sandbox = doc_root != STATIC_URL

            status = SubscriptionStatus.WIP
        elif status == SubscriptionStatus.NOT_FOUND:
            # check database (check will invalidate any out of date
            # subscriptions)
            has_sub, user_sub, expired_sub = \
                user_has_subscription(request.user, last_expired=True)
            if has_sub:
                status = SubscriptionStatus.VALID
                expiry = user_sub.end_date
            else:
                status = SubscriptionStatus.EXPIRED
                msg = 'Subscription not found' if expired_sub is None else \
                    self.sub_expired_msg(expired_sub.end_date)

        if status != SubscriptionStatus.IGNORE:
            update_session_subscription(request, status, expiry=expiry)
        if msg:
            messages.add_message(request, messages.INFO, msg)

        if not sandbox and status in PROCESS_NORMALLY:
            response = self.get_response(request)
        else:
            response = redirect(SUB_CHOICE_ROUTE)

        # Code to be executed for each request/response after
        # the view is called.

        return response

    def sub_expired_msg(self, expired_date: datetime):
        """ Generate expired message text """
        return f'Subscription expired {expired_date.strftime("%c")}'


def update_session_subscription(
        request: HttpRequest, status: SubscriptionStatus,
        expiry: datetime = None):
    """
    Update the subscription info in a request session
    :param request: request
    :param status: subscription status
    :param expiry: subscription expiry
    """
    request.session[SUB_STATUS] = status
    request.session[SUB_EXPIRY] = expiry.timestamp() if expiry else 0


def clear_session_subscription(request: HttpRequest):
    """
    Clear the subscription info in a request session
    :param request: request
    """
    for key in [SUB_STATUS, SUB_EXPIRY]:
        if key in request.session:
            del request.session[key]