#  MIT License
#
#  Copyright (c) 2022 Ian Buttimer
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
#
import random
import string
from typing import Union, List, Any, Callable, Optional, TypeVar, Tuple

import environ
from enum import Enum

from django.core.exceptions import PermissionDenied
from django.db import models
from django.http import HttpRequest

# workaround for self type hints from https://peps.python.org/pep-0673/
TypeCrud = TypeVar("TypeCrud", bound="Crud")


def random_string_generator(
        size=10, chars=string.ascii_letters + string.digits):
    """
    Generate a random string.
    Based on code from https://stackoverflow.com/a/58853028/4054609
    :param size: size of string to generate
    :param chars: characters to generate string from
    :return: string
    """
    return ''.join(random.choice(chars) for _ in range(size))


def is_boolean_true(text: str) -> bool:
    """
    Check if `text` represents a boolean True value;
    'true', 'on', 'ok', 'y', 'yes', '1'
    :param text: string to check
    :return: True if represents a boolean True value, otherwise False
    """
    return str(text).lower() in environ.Env.BOOLEAN_TRUE_STRINGS


class Crud(Enum):
    """
    Enum to map standard CRUD terms to Django models default permissions
    """
    # first term in tuple is django permission, the rest are sensible
    # alternative names
    CREATE = ('add', 'create', 'new')
    READ = ('view', 'read')
    UPDATE = ('change', 'update')
    DELETE = ('delete', 'remove')

    @staticmethod
    def from_str(value: str) -> Optional[TypeCrud]:
        """
        Get enum object matching specified `string`
        :param value: string to match
        :return: Crud or None
        """
        crud = None
        value = value.lower()
        for action in Crud:
            if value in action.value:
                crud = action
                break
        return crud


def permission_name(
    model: [str, models.Model], perm_op: Union[Crud, str],
    app_label: str = None
) -> str:
    """
    Generate a permission name.
    See
    https://docs.djangoproject.com/en/4.1/topics/auth/default/#default-permissions
    :param model: model or model name
    :param perm_op: Crud operation or permission name to check
    :param app_label:
        app label for models defined outside of an application in
        INSTALLED_APPS, default none
    :return: permission string;
            `{<app_label>.}[add|change|delete|view]_<model>`
    """
    perm = f'{app_label}.' if app_label else ''
    if not isinstance(model, str):
        model = model._meta.model_name
    if isinstance(perm_op, Crud):
        perm_val = perm_op.value[0] if isinstance(perm_op.value, tuple) \
            else perm_op.value
    else:
        perm_val = perm_op
    return f'{perm}{perm_val}_{model}'


def permission_check(
        request: Union[HttpRequest], model: [str, models.Model],
        perm_op: Union[Union[Crud, str], List[Union[Crud, str]]],
        app_label: str = None, raise_ex: bool = False) -> bool:
    """
    Check request user has specified permission
    :param request: http request or user
    :param model: model or model name
    :param perm_op: Crud operation or permission name to check
    :param app_label:
        app label for models defined outside of an application in
        INSTALLED_APPS, default none
    :param raise_ex: raise exception; default False
    :return: True if user has permission
    :raises PermissionDenied if user does not have permission and `raise_ex`
        is True
    """
    # TODO including User in the arg type hint causes a circular import
    # so leave out for now

    user = request.user if isinstance(request, HttpRequest) else request
    has_perm = user.is_superuser
    if not has_perm:
        for chk_perm in ensure_list(perm_op):
            has_perm = user.has_perm(
                permission_name(model, chk_perm, app_label=app_label))
            if not has_perm:
                break

        if not has_perm and raise_ex:
            raise PermissionDenied("Insufficient permissions")
    return has_perm


def ensure_list(item: Any) -> list[Any]:
    """
    Ensure argument is returned as a list
    :param item: item(s) to return as list
    :return: list
    """
    return item if isinstance(item, list) else [item]


def find_index(
    search: List[Any], sought: Any, start: int = None, end: int = None,
    mapper: Callable[[Any], Any] = None, replace: Any = None
) -> int:
    """
    Find the index of the first occurrence of `sought` in `search`
    (at or after index `start` and before index `end`)
    :param search: list to search
    :param sought: entry to search for
    :param start: index to begin search at; default start of `search`
    :param end: index to stop search before; default end of `search`
    :param mapper: func to map `search` entries before comparison;
                default None
    :param replace: value to replace entry with if found; default None
    :return: index of `sought`
    """
    if mapper is None:
        def pass_thru(entry):
            return entry
        mapper = pass_thru
    if start is None:
        start = 0
    if end is None:
        end = len(search)

    to_search = list(
        map(mapper, search)
    ) if mapper is not None else search

    index = to_search.index(sought, start, end)

    if index >= 0 and replace is not None:
        search[index] = replace

    return index


def dict_drill(obj: dict, *args) -> Tuple[bool, Any]:
    """
    Drill into a dict object to retrieve a value
    :param obj: dict object
    :param args: attrib names
    :return: tuple of success flag and value
    """
    success = False
    value = obj
    for key in args:
        if key in value:
            value = value[key]
        else:
            value = None
            break
    else:
        success = True
    return success, value
