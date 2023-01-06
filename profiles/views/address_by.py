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
from typing import Tuple

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.views import View

from recipesnstuff.constants import PROFILES_APP_NAME
from utils import (
    Crud, READ_ONLY_CTX, SUBMIT_URL_CTX, app_template_path, reverse_q,
    namespaced_url, TITLE_CTX, redirect_on_success_or_render,
    GET, PATCH, POST, DELETE
)

from profiles.constants import (
    ADDRESS_FORM_CTX, ADDRESS_ID_ROUTE_NAME, ADDRESSES_ROUTE_NAME
)
from profiles.forms import AddressForm
from profiles.models import Address
from .address_create import render_address_form, manage_default
from .address_queries import addresses_query
from .utils import address_permission_check


TITLE_UPDATE = 'Update Address'


class AddressDetail(LoginRequiredMixin, View):
    """
    Class-based view for address get/update/delete
    """

    def get(self, request: HttpRequest, pk: int,
            *args, **kwargs) -> HttpResponse:
        """
        GET method for Address
        :param request: http request
        :param pk: id of address
        :param args: additional arbitrary arguments
        :param kwargs: additional keyword arguments
        :return: http response
        """
        address_permission_check(request, Crud.UPDATE)

        address, _ = self._get_object(pk)

        own_address_check(request, address)

        template_path, context = render_address_form(
            TITLE_UPDATE, Crud.UPDATE, **{
            SUBMIT_URL_CTX: self.url(pk),
            ADDRESS_FORM_CTX: AddressForm(instance=address)
        })
        return render(request, template_path, context=context)

    def post(self, request: HttpRequest, pk: int,
             *args, **kwargs) -> HttpResponse:
        """
        POST method to update Address
        :param request: http request
        :param pk: id of address
        :param args: additional arbitrary arguments
        :param kwargs: additional keyword arguments
        :return: http response
        """
        address_permission_check(request, Crud.UPDATE)

        address, query_param = self._get_object(pk)

        own_address_check(request, address)

        form = AddressForm(data=request.POST, instance=address)

        if form.is_valid():
            # update object
            manage_default(
                request, form.instance, save_func=lambda: form.save())
            # django autocommits changes
            # https://docs.djangoproject.com/en/4.1/topics/db/transactions/#autocommit
            success = True

            template_path, context = None, None
        else:
            template_path, context = render_address_form(
                TITLE_UPDATE, Crud.UPDATE, **{
                SUBMIT_URL_CTX: self.url(),
                ADDRESS_FORM_CTX: form
            })
            success = False

        return redirect_on_success_or_render(
            request, success,
            namespaced_url(PROFILES_APP_NAME, ADDRESSES_ROUTE_NAME),
            template_path=template_path, context=context)


    def _get_object(self, pk: int) -> Tuple[Address, dict]:
        """
        Get entity by id
        :param pk: id of entity
        :return: tuple of object and query param
        """
        query_param = {
            f'{Address.id_field()}': pk
        }
        entity = get_object_or_404(Address, **query_param)
        return entity, query_param

    def url(self, pk: int) -> str:
        """
        Get url for address update/delete
        :param pk: id of entity
        :return: url
        """
        return reverse_q(
            namespaced_url(PROFILES_APP_NAME, ADDRESS_ID_ROUTE_NAME),
            args=[pk]
        )


ACTIONS = {
    GET: 'viewed',
    PATCH: 'updated',
    POST: 'updated',
    DELETE: 'deleted'
}

def own_address_check(
        request: HttpRequest, address: Address,
        raise_ex: bool = True) -> bool:
    """
    Check request user is address owner
    :param request: http request
    :param address: address
    :param raise_ex: raise exception if not own; default True
    """
    is_own = request.user.id == address.user.id
    if not is_own and raise_ex:
        action = ACTIONS[request.method.upper()]
        raise PermissionDenied(
            f"{address.model_name_caps()}es "
            f"may only be {action} by their owners")

    return is_own
