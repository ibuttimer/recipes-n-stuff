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
from django.shortcuts import render
from django.views import View

from recipesnstuff.constants import PROFILES_APP_NAME
from utils import (
    Crud, READ_ONLY_CTX, SUBMIT_URL_CTX, app_template_path, reverse_q,
    namespaced_url, TITLE_CTX, redirect_on_success_or_render
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

        template_path, context = render_address_form(
            TITLE_NEW, **{
                SUBMIT_URL_CTX: self.url(),
                ADDRESS_FORM_CTX: AddressForm()
            })
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

            addr_ids = None     # ids of existing addresses

            addr_query = addresses_query(request.user)
            if not addr_query.exists():
                # first address so set as default
                form.instance.is_default = True
            else:
                if form.instance.is_default:
                    # setting new address as default, so clear default
                    # on existing
                    addr_ids = addr_query.values_list(
                            Address.id_field(), flat=True)

            form.save()
            # django autocommits changes
            # https://docs.djangoproject.com/en/4.1/topics/db/transactions/#autocommit
            success = True

            if addr_ids:
                # clear default on existing addresses
                Address.objects.filter(**{
                    f'{Address.id_field()}__in': addr_ids
                }).update(**{
                    f'{Address.IS_DEFAULT_FIELD}': False
                })

            template_path, context = None, None
        else:
            template_path, context = render_address_form(
                TITLE_NEW, **{
                    SUBMIT_URL_CTX: self.url(),
                    ADDRESS_FORM_CTX: form
                })
            success = False

        return redirect_on_success_or_render(
            request, success,
            namespaced_url(PROFILES_APP_NAME, ADDRESSES_ROUTE_NAME),
            template_path=template_path, context=context)

    def url(self) -> str:
        """
        Get url for address creation
        :return: url
        """
        return reverse_q(
            namespaced_url(PROFILES_APP_NAME, ADDRESS_NEW_ROUTE_NAME)
        )


def render_address_form(title: str, **kwargs) -> tuple[
        str, dict[str, Address | list[str] | AddressForm | bool]]:
    """
    Render the address template
    :param title: title
    :param kwargs: context keyword values, see get_opinion_context()
    :return: tuple of template path and context
    """
    context = {
        TITLE_CTX: title,
        READ_ONLY_CTX: kwargs.get(READ_ONLY_CTX, False),
    }

    context_form = kwargs.get(ADDRESS_FORM_CTX, None)
    if context_form:
        context[ADDRESS_FORM_CTX] = context_form
        context[SUBMIT_URL_CTX] = kwargs.get(SUBMIT_URL_CTX, None)

    return app_template_path(PROFILES_APP_NAME, "address_form.html"), context
