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

from utils import (
    reverse_q, SUBMIT_URL_CTX, app_template_path, SUBMIT_BTN_TEXT_CTX,
    namespaced_url
)

from .constants import (
    THIS_APP, SUBSCRIPTION_NEW_ROUTE_NAME, FORM_CTX, IS_NEW_CTX,
    SUBSCRIPTIONS_URL
)
from .forms import SubscriptionForm
from .models import Subscription


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
        submit_url = reverse_q(f'{THIS_APP}:{SUBSCRIPTION_NEW_ROUTE_NAME}')
        return self.render_form(request, self.init_form(SubscriptionForm()),
                                submit_url, is_new=True)

    @staticmethod
    def init_form(form: SubscriptionForm):
        """ Initialise form display """
        for field in [
            Subscription.NAME_FIELD, Subscription.DESCRIPTION_FIELD
        ]:
            if field not in form.initial:
                form.initial[field] = ""
        return form

    @staticmethod
    def render_form(request: HttpRequest, form: SubscriptionForm,
                    submit_url: str = None,
                    is_new: bool = False) -> HttpResponse:
        return render(request, app_template_path(
            THIS_APP, "subscription_form.html"), context={
            FORM_CTX: SubscriptionCreate.init_form(form),
            SUBMIT_URL_CTX: submit_url,
            SUBMIT_BTN_TEXT_CTX: _('Save'),
            IS_NEW_CTX: is_new,
        })

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """
        POST method to create Subscription
        :param request: http request
        :param args: additional arbitrary arguments
        :param kwargs: additional keyword arguments
        :return: http response
        """

        form = SubscriptionForm(data=request.POST)

        if form.is_valid():
            # save new object

            form.save()
            # django autocommits changes
            # https://docs.djangoproject.com/en/4.1/topics/db/transactions/#autocommit
            success = True
        else:
            success = False

        return redirect(
                namespaced_url(THIS_APP, SUBSCRIPTIONS_URL)
            ) if success else self.render_form(request, form, is_new=True)
