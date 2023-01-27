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
from typing import Type

from django.db.models import QuerySet, Model

from .enums import ChoiceArg
from .misc import ensure_list
from .query_params import QuerySetParams


def get_yes_no_ignore_query(
        query_set_params: QuerySetParams,
        query_key: str,
        yes_choice: [ChoiceArg, list[ChoiceArg]],
        no_choice: [ChoiceArg, list[ChoiceArg]],
        ignore_choice: [ChoiceArg, list[ChoiceArg]],
        choice: ChoiceArg,
        clazz: Type[ChoiceArg],
        raw_qs: QuerySet,
        model: Model,
        field: str
) -> bool:
    """
    Generate a query for a yes/no/ignore choice
    :param query_set_params: query params to update
    :param query_key: query term from request
    :param yes_choice: yes_choice choice in ChoiceArg
    :param no_choice: no choice in ChoiceArg
    :param ignore_choice: ignore choice in ChoiceArg
    :param choice: choice from request
    :param clazz: ChoiceArg class
    :param raw_qs: query to get item list from db
    :param model: model to query
    :param field: field in model to query
    :return: True if successfully added
    """
    success = True
    if choice in ensure_list(ignore_choice):
        query_set_params.add_all_inclusive(query_key)
    elif isinstance(choice, clazz):
        # query lookup
        query_params = {
            f'{model}.{field}__in': raw_qs
        }

        if choice in ensure_list(no_choice):
            # exclude chosen opinions
            def qs_exclude(qry_set: QuerySet) -> QuerySet:
                return qry_set.exclude(**query_params)
            query_set = qs_exclude
        elif choice in ensure_list(yes_choice):
            # only chosen opinions
            def qs_filter(qry_set: QuerySet) -> QuerySet:
                return qry_set.filter(**query_params)
            query_set = qs_filter
        else:
            query_set = None

        if query_set:
            query_set_params.add_qs_func(query_key, query_set)
        else:
            success = False

    return success
