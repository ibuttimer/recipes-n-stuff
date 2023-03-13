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
from http import HTTPStatus
from typing import Tuple

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.template.loader import render_to_string
from django.views import View
from django.views.decorators.http import require_http_methods

from checkout.basket import add_subscription_to_basket
from checkout.constants import CHECKOUT_PAY_ROUTE_NAME
from subscription.constants import (
    THIS_APP, SUBSCRIPTION_FORM_CTX, SUBSCRIPTION_ID_ROUTE_NAME,
    SUBSCRIPTIONS_ROUTE_NAME, USER_SUB_ID_SES, SUBSCRIPTION_CHOICE_ROUTE_NAME,
)
from subscription.forms import SubscriptionForm
from subscription.models import Subscription, UserSubscription, FrequencyType
from recipesnstuff.constants import CHECKOUT_APP_NAME, HOME_ROUTE_NAME
from utils import (
    Crud, SUBMIT_URL_CTX, app_template_path, reverse_q,
    namespaced_url, redirect_on_success_or_render,
    replace_inner_html_payload, GET, STATUS_CTX
)
from subscription.middleware import subscription_payment_completed
from subscription.models import SubscriptionStatus
from .subscription_create import (
    for_subscription_form_render, SubscriptionCreate
)
from .utils import subscription_permission_check, is_eligilble_for_free_trial

TITLE_UPDATE = 'Update Subscription'


class SubscriptionDetail(LoginRequiredMixin, View):
    """
    Class-based view for subscription get/update/delete
    """

    def get(self, request: HttpRequest, pk: int,
            *args, **kwargs) -> HttpResponse:
        """
        GET method for Subscription
        :param request: http request
        :param pk: id of address
        :param args: additional arbitrary arguments
        :param kwargs: additional keyword arguments
        :return: http response
        """
        subscription_permission_check(request, Crud.UPDATE)

        subscription, _ = get_subscription(pk)

        template_path, context = \
            self.render_info(SubscriptionForm(instance=subscription))

        return render(request, template_path, context=context)

    def post(self, request: HttpRequest, pk: int,
             *args, **kwargs) -> HttpResponse:
        """
        POST method to update Subscription
        :param request: http request
        :param pk: id of address
        :param args: additional arbitrary arguments
        :param kwargs: additional keyword arguments
        :return: http response
        """
        subscription_permission_check(request, Crud.UPDATE)

        subscription, query_param = get_subscription(pk)

        form = SubscriptionForm(data=request.POST, instance=subscription)

        if form.is_valid():
            # update object
            # django autocommits changes
            # https://docs.djangoproject.com/en/4.1/topics/db/transactions/#autocommit
            form.save()

            redirect_to = reverse_q(
                namespaced_url(THIS_APP, SUBSCRIPTIONS_ROUTE_NAME)
            )
            template_path, context = None, None
        else:
            redirect_to = None
            template_path, context = self.render_info(form)

        return redirect_on_success_or_render(
            request, redirect_to is not None, redirect_to=redirect_to,
            template_path=template_path, context=context)

    def render_info(self, form: SubscriptionForm) -> tuple[
            str, dict[str, Subscription | list[str] | SubscriptionForm | bool]
    ]:
        """
        Get info to render a subscription entry
        :param form: form to use
        :return: tuple of template path and context
        """
        return for_subscription_form_render(
            TITLE_UPDATE, Crud.UPDATE, **{
                SUBMIT_URL_CTX: self.url(form.instance.pk),
                SUBSCRIPTION_FORM_CTX: SubscriptionCreate.init_form(form)
            })

    def delete(self, request: HttpRequest, pk: int,
               *args, **kwargs) -> HttpResponse:
        """
        DELETE method to delete Subscription
        :param request: http request
        :param pk: id of address
        :param args: additional arbitrary arguments
        :param kwargs: additional keyword arguments
        :return: http response
        """
        subscription_permission_check(request, Crud.UPDATE)

        address, _ = get_subscription(pk)

        # TODO refactor delete modals to single template

        status = HTTPStatus.OK
        # delete address
        count, _ = address.delete()
        payload = replace_inner_html_payload(
            "#id--subscription-deleted-modal-body",
            render_to_string(
                app_template_path(
                    THIS_APP, "snippet", "subscription_delete.html"),
                context={
                    STATUS_CTX: count > 0
                },
                request=request)
        )
        if count == 0:
            status = HTTPStatus.BAD_REQUEST

        return JsonResponse(payload, status=status)

    def url(self, pk: int) -> str:
        """
        Get url for address update/delete
        :param pk: id of entity
        :return: url
        """
        return reverse_q(
            namespaced_url(THIS_APP, SUBSCRIPTION_ID_ROUTE_NAME),
            args=[pk]
        )


def get_subscription(pk: int) -> Tuple[Subscription, dict]:
    """
    Get address by specified `id`
    :param pk: id of address
    :return: tuple of object and query param
    """
    query_param = {
        f'{Subscription.id_field()}': pk
    }
    entity = get_object_or_404(Subscription, **query_param)
    return entity, query_param


@login_required
@require_http_methods([GET])
def subscription_pick(request: HttpRequest, pk: int) -> HttpResponse:
    """
    Pick a subscription
    :param request: http request
    :param pk: id of subscription to pick
    :return: response
    """
    subscription_permission_check(request, Crud.READ)

    subscription = get_object_or_404(Subscription, **{
        f'{Subscription.id_field()}': pk
    })

    if subscription.is_free_trial and \
            not is_eligilble_for_free_trial(request):
        # not eligible for free trial, need to pick paid
        messages.add_message(
            request, messages.INFO, f"You are not eligible for the "
                                    f"'{subscription.name}' subscription")
        redirect_to = namespaced_url(THIS_APP, SUBSCRIPTION_CHOICE_ROUTE_NAME)
    else:
        # assign selected subscription
        start_date = datetime.now(tz=timezone.utc)
        freq_type = FrequencyType.from_choice(subscription.frequency_type)
        assert freq_type is not None
        end_date = start_date + freq_type.timedelta(subscription.frequency)

        user_sub = UserSubscription.objects.create(**{
            f'{UserSubscription.USER_FIELD}': request.user,
            f'{UserSubscription.SUBSCRIPTION_FIELD}': subscription,
            f'{UserSubscription.START_DATE_FIELD}': start_date,
            f'{UserSubscription.END_DATE_FIELD}': end_date,
            f'{UserSubscription.STATUS_FIELD}':
                SubscriptionStatus.ACTIVE.choice if
                subscription.is_free_trial else
                SubscriptionStatus.PAYMENT_PENDING.choice
        })
        assert user_sub is not None

        request.session[USER_SUB_ID_SES] = user_sub.id

        if subscription.is_free_trial:
            subscription_payment_completed(request)
            redirect_to = HOME_ROUTE_NAME
        else:
            add_subscription_to_basket(request, subscription)
            redirect_to = namespaced_url(
                CHECKOUT_APP_NAME, CHECKOUT_PAY_ROUTE_NAME)

    return redirect(redirect_to)
