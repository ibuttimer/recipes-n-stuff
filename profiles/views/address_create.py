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
from typing import Callable

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views import View

from recipesnstuff.constants import PROFILES_APP_NAME
from utils import (
    Crud, READ_ONLY_CTX, SUBMIT_URL_CTX, app_template_path, reverse_q,
    namespaced_url, TITLE_CTX, redirect_on_success_or_render,
    PAGE_HEADING_CTX, SUBMIT_BTN_TEXT_CTX
)

from profiles.constants import (
    ADDRESS_FORM_CTX, ADDRESS_NEW_ROUTE_NAME, ADDRESSES_ROUTE_NAME
)
from profiles.forms import AddressForm
from profiles.models import Address

from .address_queries import addresses_query
from .utils import address_permission_check


TITLE_NEW = 'New Address'


class AddressCreate(LoginRequiredMixin, View):
    """
    Class-based view for address creation
    """

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """
        GET method for Address
        :param request: http request
        :param args: additional arbitrary arguments
        :param kwargs: additional keyword arguments
        :return: http response
        """
        address_permission_check(request, Crud.CREATE)

        template_path, context = self.render_info(AddressForm())

        return render(request, template_path, context=context)

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """
        POST method to update Opinion
        :param request: http request
        :param args: additional arbitrary arguments
        :param kwargs: additional keyword arguments
        :return: http response
        """
        address_permission_check(request, Crud.CREATE)

        form = AddressForm(data=request.POST)

        if form.is_valid():
            # save new object
            form.instance.user = request.user

            manage_default(
                request, form.instance, save_func=lambda: form.save())
            # django autocommits changes
            # https://docs.djangoproject.com/en/4.1/topics/db/transactions/#autocommit
            success = True

            template_path, context = None, None
        else:
            template_path, context = self.render_info(form)
            success = False

        return redirect_on_success_or_render(
            request, success,
            redirect_to=namespaced_url(
                PROFILES_APP_NAME, ADDRESSES_ROUTE_NAME),
            template_path=template_path, context=context)

    def render_info(self, form: AddressForm):
        """
        Get info to render an address form
        :param form: form to use
        :return: tuple of template path and context
        """
        return for_address_form_render(
            TITLE_NEW, Crud.CREATE, **{
                SUBMIT_URL_CTX: self.url(),
                ADDRESS_FORM_CTX: form
            })

    def url(self) -> str:
        """
        Get url for address creation
        :return: url
        """
        return reverse_q(
            namespaced_url(PROFILES_APP_NAME, ADDRESS_NEW_ROUTE_NAME)
        )


SUBMIT_BTN_TEXT = {
    Crud.CREATE: 'Save',
    Crud.UPDATE: 'Update',
    Crud.DELETE: 'Delete',
    Crud.READ: 'Close',
}


def for_address_form_render(
        title: str, action: Crud, **kwargs: object
) -> tuple[str, dict[str, Address | list[str] | AddressForm | bool]]:
    """
    Get the template and context to Render the address template
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

    context_form = kwargs.get(ADDRESS_FORM_CTX, None)
    if context_form:
        context[ADDRESS_FORM_CTX] = context_form
        context[SUBMIT_URL_CTX] = kwargs.get(SUBMIT_URL_CTX, None)

    return app_template_path(PROFILES_APP_NAME, "address_form.html"), context


def manage_default(
        request: HttpRequest, instance: Address, save_func: Callable = None):
    """
    Manage default address for user
    :param request: http request
    :param instance: address being added/updated
    :param save_func: save instance function; default None
    """
    addr_ids = None     # ids of existing addresses

    addr_query = addresses_query(request.user)
    if not addr_query.exists():
        # only address so set as default
        instance.is_default = True
    else:
        if instance.is_default:
            # setting new address as default, so clear default
            # on existing
            if instance.pk:
                addr_query = addr_query.exclude(**{
                    f'{Address.id_field()}': instance.pk
                })

            addr_ids = list(
                addr_query.values_list(Address.id_field(), flat=True)
            )

    if save_func:
        save_func()

    if addr_ids:
        # clear default on existing addresses
        Address.objects.filter(**{
            f'{Address.id_field()}__in': addr_ids
        }).update(**{
            f'{Address.IS_DEFAULT_FIELD}': False
        })
