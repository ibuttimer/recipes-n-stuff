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

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.views import View
from django.utils.translation import gettext_lazy as _

from base.constants import SUBMIT_BTN_TEXT
from utils import (
    Crud, READ_ONLY_CTX, SUBMIT_URL_CTX, app_template_path, reverse_q,
    namespaced_url, TITLE_CTX, redirect_on_success_or_render,
    PAGE_HEADING_CTX, SUBMIT_BTN_TEXT_CTX, USER_QUERY
)

from subscription.constants import (
    THIS_APP, SUBSCRIPTION_NEW_ROUTE_NAME,
    SUBSCRIPTION_FORM_CTX, SUBSCRIPTIONS_ROUTE_NAME
)
from subscription.forms import SubscriptionForm
from subscription.models import Subscription

from .utils import subscription_permission_check

TITLE_NEW = 'New Subscription'

class SubscriptionCreate(LoginRequiredMixin, View):
    """
    Class-based view for subscription creation
    """

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """
        GET method for Subscription
        :param request: http request
        :param args: additional arbitrary arguments
        :param kwargs: additional keyword arguments
        :return: http response
        """
        subscription_permission_check(request, Crud.CREATE)

        template_path, context = self.render_info(SubscriptionForm())

        return render(request, template_path, context=context)

    @staticmethod
    def init_form(form: SubscriptionForm):
        """ Initialise form display """
        for field in [
            Subscription.NAME_FIELD, Subscription.DESCRIPTION_FIELD
        ]:
            if field not in form.initial:
                form.initial[field] = ""
        return form

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """
        POST method to create Subscription
        :param request: http request
        :param args: additional arbitrary arguments
        :param kwargs: additional keyword arguments
        :return: http response
        """
        subscription_permission_check(request, Crud.CREATE)

        form = SubscriptionForm(data=request.POST)

        if form.is_valid():
            # save new object

            form.save()
            # django autocommits changes
            # https://docs.djangoproject.com/en/4.1/topics/db/transactions/#autocommit

            redirect_to = namespaced_url(THIS_APP, SUBSCRIPTIONS_ROUTE_NAME)
            template_path, context = None, None
        else:
            redirect_to = None
            template_path, context = self.render_info(form)

        return redirect_on_success_or_render(
            request, redirect_to is not None, redirect_to=redirect_to,
            template_path=template_path, context=context)

    def render_info(self, form: SubscriptionForm):
        """
        Get info to render a subscription form
        :param form: form to use
        :return: tuple of template path and context
        """
        return for_subscription_form_render(
            TITLE_NEW, Crud.CREATE, **{
                SUBMIT_URL_CTX: self.url(),
                SUBSCRIPTION_FORM_CTX: form
            })

    def url(self) -> str:
        """
        Get url for address creation
        :return: url
        """
        return reverse_q(
            namespaced_url(THIS_APP, SUBSCRIPTION_NEW_ROUTE_NAME)
        )


def for_subscription_form_render(
        title: str, action: Crud, **kwargs: object
) -> tuple[str, dict[str, Subscription | list[str] | SubscriptionForm | bool]]:
    """
    Get the template and context to Render the subscription template
    :param title: title
    :param action: form action
    :param kwargs: context keyword values, see get_opinion_context()
    :return: tuple of template path and context
    """
    context = {
        TITLE_CTX: title,
        PAGE_HEADING_CTX: title,
        SUBMIT_BTN_TEXT_CTX: SUBMIT_BTN_TEXT[action],
        READ_ONLY_CTX: kwargs.get(READ_ONLY_CTX, False),
    }

    context_form = kwargs.get(SUBSCRIPTION_FORM_CTX, None)
    if context_form:
        context[SUBSCRIPTION_FORM_CTX] = context_form
        context[SUBMIT_URL_CTX] = kwargs.get(SUBMIT_URL_CTX, None)

    return app_template_path(THIS_APP, "subscription_form.html"), context
