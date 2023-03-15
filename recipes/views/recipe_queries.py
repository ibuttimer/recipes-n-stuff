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
from datetime import datetime, timezone
from enum import Enum, auto
from typing import Any, Type, Optional, Tuple, List, Union
from zoneinfo import ZoneInfo

from django.db.models import Q, QuerySet, Prefetch, Model
from django.shortcuts import get_object_or_404

from checkout.models import Currency
from order.models import OrderProduct
from recipes.constants import (
    KEYWORD_QUERY, CATEGORY_QUERY, AUTHOR_QUERY, INGREDIENT_QUERY
)
from recipes.models import (
    Recipe, Ingredient, Instruction, RecipeIngredient, Keyword, Category
)
from user.models import User
from utils import (
    SEARCH_QUERY, DATE_QUERIES,
    regex_matchers, regex_date_matchers, QuerySetParams,
    TERM_GROUP, KEY_TERM_GROUP, DATE_QUERY_GROUP, DATE_KEY_TERM_GROUP,
    DATE_QUERY_YR_GROUP, DATE_QUERY_MTH_GROUP,
    DATE_QUERY_DAY_GROUP, USER_QUERY, get_object_and_related_or_404
)
from utils.query_params import SearchType, QueryTerm
from utils.search import MARKER_CHARS

NON_DATE_QUERIES = [
    KEYWORD_QUERY, INGREDIENT_QUERY, CATEGORY_QUERY, USER_QUERY, AUTHOR_QUERY
]
REGEX_MATCHERS = regex_matchers(NON_DATE_QUERIES)
REGEX_MATCHERS.update(regex_date_matchers())

FIELD_LOOKUPS = {
    # query param: filter lookup
    SEARCH_QUERY: '',
    KEYWORD_QUERY: f'{Recipe.KEYWORDS_FIELD}__in',
    INGREDIENT_QUERY: f'{Recipe.INGREDIENTS_FIELD}__in',
    CATEGORY_QUERY: f'{Recipe.CATEGORY_FIELD}__{Category.NAME_FIELD}__iexact',
    AUTHOR_QUERY: f'{Recipe.AUTHOR_FIELD}__{User.USERNAME_FIELD}__icontains',
    # CATEGORY_QUERY: f'{Opinion.CATEGORIES_FIELD}__in',
    # ON_OR_AFTER_QUERY: f'{Opinion.SEARCH_DATE_FIELD}__date__gte',
    # ON_OR_BEFORE_QUERY: f'{Opinion.SEARCH_DATE_FIELD}__date__lte',
    # AFTER_QUERY: f'{Opinion.SEARCH_DATE_FIELD}__date__gt',
    # BEFORE_QUERY: f'{Opinion.SEARCH_DATE_FIELD}__date__lt',
    # EQUAL_QUERY: f'{Opinion.SEARCH_DATE_FIELD}__date',
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
    # FILTER_QUERY, REVIEW_QUERY
]

SEARCH_REGEX = [
    # regex,            query param, regex match group, key & regex match grp
    (REGEX_MATCHERS[q], q,           TERM_GROUP,        KEY_TERM_GROUP)
    for q in NON_DATE_QUERIES
]
SEARCH_REGEX.extend([
    # regex,            query param, regex match group, key & regex match grp
    (REGEX_MATCHERS[q], q,           DATE_QUERY_GROUP,  DATE_KEY_TERM_GROUP)
    for q in DATE_QUERIES
])


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
    elif query == KEYWORD_QUERY:
        add_keyword_query(query_set_params, value)
    elif query == INGREDIENT_QUERY:
        add_ingredient_query(query_set_params, value)
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
            if query == KEYWORD_QUERY:
                add_keyword_query(query_set_params, match.group(group))
            elif query == INGREDIENT_QUERY:
                add_ingredient_query(query_set_params, match.group(group))
            elif query in DATE_QUERIES:
                success = get_date_query(query_set_params, query, *[
                    match.group(idx) for idx in [
                        DATE_QUERY_YR_GROUP, DATE_QUERY_MTH_GROUP,
                        DATE_QUERY_DAY_GROUP
                    ]
                ])
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
            to_query = [KEYWORD_QUERY, INGREDIENT_QUERY]
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
                if qry == KEYWORD_QUERY:
                    add_keyword_query(
                        query_set_params, or_q[qry], query_type=QueryTerm.OR,
                        query=qry, key=key)
                elif qry == INGREDIENT_QUERY:
                    add_ingredient_query(
                        query_set_params, or_q[qry], query_type=QueryTerm.OR,
                        query=qry, key=key)
                else:
                    # simple lookup
                    query_set_params.add_or_lookup(key, Q(_connector=Q.OR, **{
                        FIELD_LOOKUPS[qry]: term for term in or_q[qry]
                    }))

    return query_set_params


def add_m2m_name_query(query_set_params: QuerySetParams,
                       value: Union[str, list], model: Model, name_field: str,
                       query: str, key: str = None,
                       query_type: QueryTerm = QueryTerm.AND) -> None:
    """
    Get a many-to-many query based on name
    :param query_set_params: query params to update
    :param model: Model of objects to query
    :param name_field: name of the `name` field in sub-model
    :param value: name or part thereof
    :param query: query key
    :param key: query params key; default same as query key
    :param query_type: query type to add; default QueryTerm.AND
    """
    # need inner queryset to get list of linked model objects with names
    # like the search term and then look for recipes with those
    # objects
    # https://docs.djangoproject.com/en/4.1/ref/models/querysets/#icontains
    lookup = f'{name_field}__icontains'
    if not key:
        key = query
    if query_type == QueryTerm.OR:
        # queryset to get list of linked model objects with names like any of
        # the parts of the search term
        words_qs = model.objects.filter(
            Q(_connector=Q.OR, **{
                lookup: term for term in value
            })
        )
        inner_qs = Q(_connector=Q.OR, **{
            FIELD_LOOKUPS[query]: words_qs
        })
    else:
        # queryset to get list of linked model objects with names like the
        # search term
        inner_qs = model.objects.filter(**{
            lookup: value
        })

    query_set_params.add_query_term(
        query_type, key, value=inner_qs, term=FIELD_LOOKUPS[query])


def add_keyword_query(query_set_params: QuerySetParams,
                      value: Union[str, list],
                      query: str = KEYWORD_QUERY, key: str = None,
                      query_type: QueryTerm = QueryTerm.AND) -> None:
    """
    Get a keyword query based on name
    :param query_set_params: query params to update
    :param value: keyword name or part thereof
    :param query: query key
    :param key: query params key; default same as query key
    :param query_type: query type to add; default QueryTerm.AND
    """
    # need inner queryset to get list of keywords with names
    # like the search term and then look for recipes with those
    # keywords
    # https://docs.djangoproject.com/en/4.1/ref/models/querysets/#icontains
    add_m2m_name_query(query_set_params, value, Keyword, Keyword.NAME_FIELD,
                       query, key=key, query_type=query_type)


def add_ingredient_query(query_set_params: QuerySetParams,
                         value: Union[str, list],
                         query: str = INGREDIENT_QUERY, key: str = None,
                         query_type: QueryTerm = QueryTerm.AND) -> None:
    """
    Get an ingredient query based on name
    :param query_set_params: query params to update
    :param value: name or part thereof
    :param query: query key
    :param key: query params key; default same as query key
    :param query_type: query type to add; default QueryTerm.AND
    """
    # need inner queryset to get list of recipe ingredients whose ingredients
    # have names like the search term and then look for recipes with those
    # keywords
    # https://docs.djangoproject.com/en/4.1/ref/models/querysets/#icontains
    add_m2m_name_query(query_set_params, value, Ingredient,
                       Ingredient.NAME_FIELD,
                       query, key=key, query_type=query_type)


def get_date_query(query_set_params: QuerySetParams,
                   query: str, year: str, month: str, day: str) -> bool:
    """
    Get a date query
    :param query_set_params: query params to update
    :param query: query key
    :param year: year
    :param month: month
    :param day: day
    :return: True if successfully added
    """
    success = True
    try:
        date = datetime(
            int(year), int(month), int(day), tzinfo=ZoneInfo("UTC")
        )
        query_set_params.add_and_lookup(
            query, FIELD_LOOKUPS[query], date)
    except ValueError:
        # ignore invalid date
        # TODO add errors to QuerySetParams
        # so they can be returned to user
        success = False
    return success


def _get_recipe_contents(
        recipe_id: int,
        field: str) -> Optional[List[Ingredient | Instruction]]:
    """
    Get the list of contents
    :param recipe_id: id of recipe
    :return: list of contents or None if recipe not found
    """
    recipe = Recipe.objects.prefetch_related(field).get(**{
        f'{Recipe.id_field()}': recipe_id
    })
    if recipe:
        contents = recipe.ingredients if field == Recipe.INGREDIENTS_FIELD \
            else recipe.instructions if field == Recipe.INSTRUCTIONS_FIELD \
            else recipe.keywords if field == Recipe.KEYWORDS_FIELD else None
    else:
        contents = None

    return list(contents.all()) if contents else None


def get_recipe_ingredients(recipe_id: int) -> Optional[List[Ingredient]]:
    """
    Get the list of ingredients
    :param recipe_id: id of recipe
    :return: list of ingredients or None if recipe not found
    """
    return _get_recipe_contents(recipe_id, Recipe.INGREDIENTS_FIELD)


def get_recipe_instructions(recipe_id: int) -> Optional[List[Instruction]]:
    """
    Get the list of instructions
    :param recipe_id: id of recipe
    :return: list of instructions or None if recipe not found
    """
    return _get_recipe_contents(recipe_id, Recipe.INSTRUCTIONS_FIELD)


def get_recipe(
        pk: int, related: Optional[List[str]] = None) -> Tuple[Recipe, dict]:
    """
    Get recipe by specified `id`
    :param pk: id of recipe
    :param related: list of related fields to prefetch; default None
    :return: tuple of object and query param
    :raises Http404 if not found
    """
    query_param = {
        f'{Recipe.id_field()}': pk
    }
    entity = get_object_and_related_or_404(
        Recipe, **query_param, related=related)
    return entity, query_param


def get_recipe_ingredients_list(
        recipe: Union[int, Recipe],
        order_by: str = RecipeIngredient.INDEX_FIELD,
        prefetch_related: bool = True
        ) -> List[RecipeIngredient]:
    """
    Get recipe ingredients for the specified `recipe`
    :param recipe: recipe object or its id
    :param order_by: order by; default index field
    :param prefetch_related: prefetch related flag, default True
    :return: tuple of object and query param
    """
    query_param = {
        f'{RecipeIngredient.RECIPE_FIELD}':
            get_recipe(recipe) if isinstance(recipe, int) else recipe
    }

    measures_prefetch = Prefetch(
        Ingredient.MEASURE_FIELD, queryset=Ingredient.objects.all())
    ingredients_prefetch = Prefetch(
        RecipeIngredient.INGREDIENT_FIELD,
        queryset=measures_prefetch.queryset.all())

    return list(
        RecipeIngredient.objects.prefetch_related(
            ingredients_prefetch
        ).filter(**query_param).order_by(order_by).all()
    )


def get_recipe_ingredient(pk: int) -> Tuple[RecipeIngredient, dict]:
    """
    Get recipe ingredient by specified `id`
    :param pk: id of recipe ingredient
    :return: tuple of object and query param
    """
    query_param = {
        f'{RecipeIngredient.id_field()}': pk
    }
    entity = get_object_or_404(RecipeIngredient, **query_param)
    return entity, query_param


def get_recipe_instruction(pk: int) -> Tuple[Instruction, dict]:
    """
    Get recipe instruction by specified `id`
    :param pk: id of recipe instruction
    :return: tuple of object and query param
    """
    query_param = {
        f'{Instruction.id_field()}': pk
    }
    entity = get_object_or_404(Instruction, **query_param)
    return entity, query_param


def get_recipe_box_product(pk: int,
                           get_or_404: bool = True) -> Tuple[OrderProduct, Currency]:
    """
    Get the ingredient box product for a recipe
    :param pk: id of recipe
    :param get_or_404: get ot 404 flag; default True
    :return: tuple of order product and base currency
    """
    query_param = {
        f'{OrderProduct.RECIPE_FIELD}': pk
    }
    entity = get_object_or_404(OrderProduct, **query_param) \
        if get_or_404 else OrderProduct.objects.filter(**query_param).first()
    currency = Currency.objects.get(**{
        f'{Currency.CURRENCY_CODE_FIELD}': entity.base_currency
    }) if entity else None
    return entity, currency


def get_recipe_count(user: Union[User, int, str]) -> int:
    """
    Get the recipe count for the specified user
    :param user: id/username of user or user instance
    :return: recipe count
    """
    if not isinstance(user, User):
        param = User.id_field() if isinstance(user, int) else \
            User.USERNAME_FIELD
        user = get_object_or_404(User, **{
            f'{param}': user
        })

    return Recipe.objects.filter(**{
        f'{Recipe.AUTHOR_FIELD}': user
    }).count()


def nutritional_info_valid(pk: int) -> bool:
    """
    Check the nutritional info for a recipe is valid
    :param pk: id of recipe
    :return: True if valid
    """
    fields = Recipe.objects.filter(**Recipe.id_field_query(pk)).values_list(
        *Recipe.nutritional_fields()
    )
    return any(fields.first())
