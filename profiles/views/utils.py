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
from typing import Union, List

from django.core.exceptions import PermissionDenied
from django.http import HttpRequest
from django.template.loader import render_to_string

from base import (
    render_level_info_modal, InfoModalLevel, InfoModalTemplate, IDENTIFIER_CTX
)
from profiles.constants import COUNT_CTX
from profiles.models import Address
from recipesnstuff import PROFILES_APP_NAME, BASE_APP_NAME
from utils import (
    Crud, permission_check, app_template_path, GET, PATCH, POST, DELETE,
    ModelMixin
)


def address_permission_check(
        request: HttpRequest,
        perm_op: Union[Union[Crud, str], List[Union[Crud, str]]],
        raise_ex: bool = True) -> bool:
    """
    Check request user has specified permission
    :param request: http request
    :param perm_op: Crud operation or permission name to check
    :param raise_ex: raise exception; default True
    """
    return permission_check(request, Address, perm_op,
                            app_label=PROFILES_APP_NAME, raise_ex=raise_ex)


def address_dflt_unmod_snippets(count: int) -> List[str]:
    """
    Generate html snippets to display address default unmodifiable info modal
    :param count: number of addresses
    :return: list of html snippets
    """
    identifier = 'dflt-addr-unmod'
    return [
        render_level_info_modal(
            InfoModalLevel.WARN,
            InfoModalTemplate(
                app_template_path(
                    PROFILES_APP_NAME, "snippet",
                    "address_default_unmodifiable.html"),
                context={
                    COUNT_CTX: count,
                }
            ),
            identifier
        ),
        render_to_string(
            app_template_path(
                BASE_APP_NAME, "snippet",
                "show_info_modal_on_ready.html"),
            context={
                IDENTIFIER_CTX: identifier
            }
        )
    ]


ACTIONS = {
    GET: 'viewed',
    PATCH: 'updated',
    POST: 'updated',
    DELETE: 'deleted'
}


def raise_permission_denied(
        request: HttpRequest, model: ModelMixin, plural: str = 's'):
    """
    Raise a PermissionDenied exception
    :param request: http request
    :param model: model
    :param plural: model name pluralising addition; default 's'
    :raises: PermissionDenied
    """
    action = ACTIONS[request.method.upper()]
    raise PermissionDenied(
        f"{model.model_name_caps()}{plural} may only be {action} by "
        f"their owners")