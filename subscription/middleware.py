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
import jsonpickle

from checkout.constants import (
    CHECKOUT_CREATE_PAYMENT_ROUTE_NAME, CHECKOUT_PAY_ROUTE_NAME,
    CHECKOUT_UPDATE_BASKET_ROUTE_NAME, CHECKOUT_PAID_ROUTE_NAME
)
from recipesnstuff.constants import LOGOUT_ROUTE_NAME, CHECKOUT_APP_NAME
from recipesnstuff.settings import STATIC_URL
from subscription.views.subscription_queries import user_has_subscription
from utils import namespaced_url, resolve_req

from .constants import (
    THIS_APP, SUBSCRIPTION_CHOICE_ROUTE_NAME, SUBSCRIPTION_PICK_ROUTE_NAME,
    USER_SUB_ID_SES
)
from .models import UserSubscription, SubscriptionStatus

SUB_EXPIRY = 'sub_expiry'   # subscription expiry date
SUB_STATUS = 'sub_status'   # subscription status
SUB_TRIAL = 'sub_trial'     # trail subscription


# workaround for self type hints from https://peps.python.org/pep-0673/
TypeSessionSubStatus = \
    TypeVar("TypeSessionSubStatus", bound="SessionSubStatus")


class SessionSubStatus(Enum):
    """ Enum represent subscription status """
    NOT_FOUND = auto()
    EXPIRED = auto()
    WIP = auto()
    VALID = auto()
    IGNORE = auto()     # anonymous user

    @staticmethod
    def from_jsonable(jsonable: dict) -> TypeSessionSubStatus:
        """
        Convert json representation to enum
        :param jsonable: json representation
        :return: SessionSubStatus
        """
        status = jsonable
        if not isinstance(status, SessionSubStatus):
            status = jsonpickle.decode(jsonable)
        return status

    def __json__(self):
        """ Return a built-in object that is naturally jsonable """
        return jsonpickle.encode(self)


PROCESS_NORMALLY = [
    SessionSubStatus.VALID, SessionSubStatus.WIP,
    SessionSubStatus.IGNORE
]
SUB_CHOICE_ROUTE = namespaced_url(THIS_APP, SUBSCRIPTION_CHOICE_ROUTE_NAME)
NO_SUB_SANDBOX = [
    # no subscription restricted to choose subscription, payment or logout
    SUB_CHOICE_ROUTE, LOGOUT_ROUTE_NAME,
    namespaced_url(THIS_APP, SUBSCRIPTION_PICK_ROUTE_NAME),
    namespaced_url(CHECKOUT_APP_NAME, CHECKOUT_CREATE_PAYMENT_ROUTE_NAME),
    namespaced_url(CHECKOUT_APP_NAME, CHECKOUT_UPDATE_BASKET_ROUTE_NAME),
    namespaced_url(CHECKOUT_APP_NAME, CHECKOUT_PAY_ROUTE_NAME),
    namespaced_url(CHECKOUT_APP_NAME, CHECKOUT_PAID_ROUTE_NAME)
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
        is_trial = False    # trial subscription
        sandbox = False     # stay in subscription sandbox flag
        status = SessionSubStatus.IGNORE if request.user.is_superuser else \
            request.session.get(SUB_STATUS, SessionSubStatus.NOT_FOUND) \
            if request.user.is_authenticated else SessionSubStatus.IGNORE
        status = SessionSubStatus.from_jsonable(status)

        if status == SessionSubStatus.VALID:
            # check expiry date
            expiry = datetime.fromtimestamp(
                request.session[SUB_EXPIRY], tz=timezone.utc)
            is_trial = request.session[SUB_TRIAL]
            if expiry < datetime.now(tz=timezone.utc):
                status = SessionSubStatus.EXPIRED
                msg = self.sub_expired_msg(expiry, was_trial=is_trial)
        elif status in [SessionSubStatus.WIP, SessionSubStatus.EXPIRED]:
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

            status = SessionSubStatus.WIP
        elif status == SessionSubStatus.NOT_FOUND:
            # check database (check will invalidate any out of date
            # subscriptions)
            has_sub, user_sub, expired_sub = \
                user_has_subscription(request.user, last_expired=True)
            if has_sub:
                status = SessionSubStatus.VALID
                expiry = user_sub.end_date
                is_trial = user_sub.is_free_trial
            else:
                status = SessionSubStatus.EXPIRED
                msg = 'Subscription not found' if expired_sub is None else \
                    self.sub_expired_msg(expired_sub.end_date,
                                         was_trial=expired_sub.is_free_trial)

        if status != SessionSubStatus.IGNORE:
            update_session_subscription(
                request, status, expiry=expiry, is_trial=is_trial)
        if msg:
            messages.add_message(request, messages.INFO, msg)

        if not sandbox and status in PROCESS_NORMALLY:
            response = self.get_response(request)
        else:
            response = redirect(SUB_CHOICE_ROUTE)

        # Code to be executed for each request/response after
        # the view is called.

        return response

    def sub_expired_msg(self, expired_date: datetime, was_trial: bool = False):
        """ Generate expired message text """
        sub_type = 'Trial subscription' if was_trial else 'Subscription'
        return f'{sub_type} expired {expired_date.strftime("%c")}'


def update_session_subscription(
        request: HttpRequest, status: SessionSubStatus,
        expiry: datetime = None, is_trial: bool = False):
    """
    Update the subscription info in a request session
    :param request: request
    :param status: subscription status
    :param expiry: subscription expiry
    :param is_trial: is trial subscription flag
    """
    request.session[SUB_STATUS] = status
    request.session[SUB_EXPIRY] = expiry.timestamp() if expiry else 0
    request.session[SUB_TRIAL] = is_trial


def subscription_payment_completed(request: HttpRequest):
    """
    Update status following completion of subscription payment
    :param request: http request
    """
    user_sub = UserSubscription.objects.get(**{
        f'{UserSubscription.id_field()}':
            int(request.session[USER_SUB_ID_SES]),
    })

    user_sub.status = SubscriptionStatus.ACTIVE.choice
    user_sub.save()

    # update session
    update_session_subscription(request, SessionSubStatus.VALID,
                                user_sub.end_date)


def clear_session_subscription(request: HttpRequest):
    """
    Clear the subscription info in a request session
    :param request: request
    """
    for key in [SUB_STATUS, SUB_EXPIRY]:
        if key in request.session:
            del request.session[key]
