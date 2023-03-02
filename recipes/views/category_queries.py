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
#
from enum import Enum, auto
from typing import Any, Optional, Tuple, List, Union

from django.core.exceptions import BadRequest
from django.db.models import Q

from recipes.constants import LETTER_QUERY
from recipes.models import (
    Recipe, Category
)
from user.models import User
from utils import (
    SEARCH_QUERY, regex_matchers, QuerySetParams,
    TERM_GROUP, KEY_TERM_GROUP, get_object_and_related_or_404
)
from utils.query_params import SearchType
from utils.search import MARKER_CHARS

NON_DATE_QUERIES = [LETTER_QUERY]
REGEX_MATCHERS = regex_matchers(NON_DATE_QUERIES)

FIELD_LOOKUPS = {
    # query param: filter lookup
    SEARCH_QUERY: '',
    LETTER_QUERY: f'{Category.NAME_FIELD}__istartswith',    # basic a-z lookup
}
# priority order list of query terms
FILTERS_ORDER = [
    # search is a shortcut filter, if search is specified nothing
    # else is checked after therefore must be first
    SEARCH_QUERY,
]
ALWAYS_FILTERS = [
    # always applied items
    # option.query for option in OPINION_APPLIED_DEFAULTS_QUERY_ARGS
]
FILTERS_ORDER.extend(
    [q for q in FIELD_LOOKUPS if q not in FILTERS_ORDER]
)
# complex queries which require more than a simple lookup or context-related
NON_LOOKUP_ARGS = [
    LETTER_QUERY    # complex non a-z query
]

SEARCH_REGEX = [
    # regex,            query param, regex match group, key & regex match grp
    (REGEX_MATCHERS[q], q,           TERM_GROUP,        KEY_TERM_GROUP)
    for q in NON_DATE_QUERIES
]


class QueryParam(Enum):
    """ Enum representing options for QuerySet creation """
    FILTER = auto()
    EXCLUDE = auto()


def get_lookup(
    query: str, value: Any, user: User,
    query_set_params: QuerySetParams = None
) -> QuerySetParams:
    """
    Get the query lookup for the specified value
    :param query: request query argument
    :param value: argument value
    :param user: current user
    :param query_set_params: query set params
    :return: query set params
    """
    if query_set_params is None:
        query_set_params = QuerySetParams()
    if value is None:
        return query_set_params

    if query == SEARCH_QUERY:
        query_set_params = get_search_term(
            value, user, query_set_params=query_set_params)
    elif query == LETTER_QUERY:
        add_letter_query(query_set_params, value)
    elif query not in NON_LOOKUP_ARGS and value:
        query_set_params.add_and_lookup(query, FIELD_LOOKUPS[query], value)
    # else no value or complex query term handled elsewhere

    return query_set_params


def get_search_term(
    value: str, user: User, query_set_params: QuerySetParams = None
) -> QuerySetParams:
    """
    Generate search terms for specified input value
    :param value: search value
    :param user: current user
    :param query_set_params: query set params
    :return: query set params
    """
    if query_set_params is None:
        query_set_params = QuerySetParams()
    if value is None:
        return query_set_params

    for regex, query, group, key_val_group in SEARCH_REGEX:
        match = regex.match(value)
        if match:
            success = True
            if query == LETTER_QUERY:
                add_letter_query(query_set_params, value)
            elif query not in NON_LOOKUP_ARGS:
                query_set_params.add_and_lookup(
                    query, FIELD_LOOKUPS[query], match.group(group))
            else:
                # complex query term handled elsewhere
                success = False

            save_term_func = query_set_params.add_search_term if success \
                else query_set_params.add_invalid_term
            save_term_func(match.group(key_val_group))

    if query_set_params.is_empty and value:
        query_set_params.search_type = SearchType.FREE if not any(
            list(
                map(lambda x: x in value, MARKER_CHARS)
            )
        ) else SearchType.UNKNOWN

        if query_set_params.search_type == SearchType.FREE:
            # no delimiting chars, so search keyword for
            # any of the search terms
            to_query = []
            or_q = {}
            for term in value.split():
                if len(or_q) == 0:
                    or_q = {q: [term] for q in to_query}
                else:
                    for q in to_query:
                        or_q[q].append(term)

            # https://docs.djangoproject.com/en/4.1/topics/db/queries/#complex-lookups-with-q

            # OR queries of keyword and content contains terms
            # e.g. [
            #   "WHERE ("keyword") LIKE '<term>'",
            #   "WHERE ("content") LIKE '<term>'"
            # ]
            for qry in to_query:
                key = '-'.join(to_query)
                # simple lookup
                query_set_params.add_or_lookup(key, Q(_connector=Q.OR, **{
                    FIELD_LOOKUPS[qry]: term for term in or_q[qry]
                }))

    return query_set_params


def get_category(
        pk: int, related: Optional[List[str]] = None) -> Tuple[Recipe, dict]:
    """
    Get category by specified `id`
    :param pk: id of recipe
    :param related: list of related fields to prefetch; default None
    :return: tuple of object and query param
    :raises Http404 if not found
    """
    query_param = {
        f'{Category.id_field()}': pk
    }
    entity = get_object_and_related_or_404(
        Category, **query_param, related=related)
    return entity, query_param


def add_letter_query(query_set_params: QuerySetParams, letter: str) -> None:
    """
    Get the keyword query
    :param query_set_params: query params to update
    :param letter: first letter of required categories
    """
    if not letter:
        raise BadRequest('Malformed request; query not specified')
    if len(letter) > 1:
        letter = letter[:1]
    letter = letter.lower()
    if letter.isalpha():
        query_set_params.add_and_lookup(
            LETTER_QUERY, FIELD_LOOKUPS[LETTER_QUERY], letter)
    else:
        # lookup names not beginning with alphabetic chars using
        # custom lookup INotSimilarTo
        query_set_params.add_and_lookup(
            LETTER_QUERY, f'{Category.NAME_FIELD}__inotsimilarto', "[a-z]%")
