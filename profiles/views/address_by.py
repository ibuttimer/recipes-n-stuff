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
from http import HTTPStatus
from typing import Tuple

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.template.loader import render_to_string
from django.views import View
from django.views.decorators.http import require_http_methods

from base import (
    InfoModalLevel, InfoModalTemplate, level_info_modal_payload,
)
from profiles.constants import (
    ADDRESS_FORM_CTX, ADDRESS_ID_ROUTE_NAME, COUNT_CTX, THIS_APP
)
from profiles.forms import AddressForm
from profiles.models import Address
from utils import (
    Crud, SUBMIT_URL_CTX, app_template_path, reverse_q,
    namespaced_url, redirect_on_success_or_render,
    replace_inner_html_payload, redirect_payload,
    GET, PATCH, POST, DELETE, STATUS_CTX, USER_QUERY
)
from .address_create import (
    for_address_form_render, manage_default, get_user_addresses_url
)
from .address_queries import addresses_query, DEFAULT_ADDRESS_QUERY
from .utils import address_permission_check
from base.utils import raise_permission_denied

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

        address, _ = get_address(pk)

        own_address_check(request, address)

        template_path, context = \
            self.render_info(AddressForm(instance=address))

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

        address, query_param = get_address(pk)
        is_default = address.is_default

        own_address_check(request, address)

        form = AddressForm(data=request.POST, instance=address)

        if form.is_valid():

            query_kwargs = {}
            if is_default and not form.instance.is_default:
                # prevent default address change; display info modal
                form.instance.is_default = is_default
                query_kwargs = {
                    DEFAULT_ADDRESS_QUERY:
                        addresses_query(request.user).count(),
                }

                # TODO alternative to passing default addr query param
                # passing default addr query param means that a reload
                # displays the modal again but can't pass a context to
                # redirect so ?

            # update object
            manage_default(
                request, form.instance, save_func=lambda: form.save())
            # django autocommits changes
            # https://docs.djangoproject.com/en/4.1/topics/db/transactions/#autocommit

            redirect_to = get_user_addresses_url(
                request, query_kwargs=query_kwargs)
            template_path, context = None, None
        else:
            redirect_to = None
            template_path, context = self.render_info(form)

        return redirect_on_success_or_render(
            request, redirect_to is not None, redirect_to=redirect_to,
            template_path=template_path, context=context)

    def render_info(self, form: AddressForm) -> tuple[
            str, dict[str, Address | list[str] | AddressForm | bool]]:
        """
        Get info to render an address entry
        :param form: form to use
        :return: tuple of template path and context
        """
        return for_address_form_render(
            TITLE_UPDATE, Crud.UPDATE, **{
                SUBMIT_URL_CTX: self.url(form.instance.pk),
                ADDRESS_FORM_CTX: form
            })

    def delete(self, request: HttpRequest, pk: int,
               *args, **kwargs) -> HttpResponse:
        """
        DELETE method to delete Address
        :param request: http request
        :param pk: id of address
        :param args: additional arbitrary arguments
        :param kwargs: additional keyword arguments
        :return: http response
        """
        address_permission_check(request, Crud.UPDATE)

        address, _ = get_address(pk)

        own_address_check(request, address)

        status = HTTPStatus.OK
        if address.is_default:
            # prevent default address delete; display info modal
            payload = level_info_modal_payload(
                InfoModalLevel.WARN,
                InfoModalTemplate(
                    app_template_path(
                        THIS_APP, "snippet",
                        "default_address_undeletable.html"),
                    context={
                        COUNT_CTX: addresses_query(request.user).count(),
                    }
                ),
                'dflt-addr-del'
            )
        else:
            # delete address
            count, _ = address.delete()
            payload = replace_inner_html_payload(
                "#id--address-deleted-modal-body",
                render_to_string(
                    app_template_path(
                        THIS_APP, "snippet", "address_delete.html"),
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
            namespaced_url(THIS_APP, ADDRESS_ID_ROUTE_NAME), args=[pk]
        )


def get_address(pk: int) -> Tuple[Address, dict]:
    """
    Get address by specified `id`
    :param pk: id of address
    :return: tuple of object and query param
    """
    query_param = {
        f'{Address.id_field()}': pk
    }
    entity = get_object_or_404(Address, **query_param)
    return entity, query_param


@login_required
@require_http_methods([PATCH])
def address_default(request: HttpRequest, pk: int) -> HttpResponse:
    """
    View function to update opinion status.
    :param request: http request
    :param pk:      id of opinion
    :return: response
    """
    address_permission_check(request, Crud.UPDATE)

    address, _ = get_address(pk)

    own_address_check(request, address)

    address.is_default = True

    # update object
    manage_default(
        request, address, save_func=lambda: address.save())

    return JsonResponse(
        redirect_payload(
            get_user_addresses_url(request)
        ),
        status=HTTPStatus.OK
    )


def own_address_check(request: HttpRequest, address: Address,
                      raise_ex: bool = True) -> bool:
    """
    Check request user is address owner
    :param request: http request
    :param address: address
    :param raise_ex: raise exception if not own; default True
    """
    is_own = request.user.id == address.user.id
    if not is_own and raise_ex:
        raise_permission_denied(request, address, plural='es')

    return is_own
