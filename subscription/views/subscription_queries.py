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
from typing import Any, Type, Optional, Tuple, List
from zoneinfo import ZoneInfo

from django.db.models import Q, QuerySet

from subscription.constants import IS_ACTIVE_QUERY
from subscription.models import (
    Subscription, UserSubscription, SubscriptionFeature
)
from user.models import User
from utils import (
    SEARCH_QUERY, DATE_QUERIES,
    regex_matchers, regex_date_matchers, QuerySetParams,
    TERM_GROUP, KEY_TERM_GROUP, DATE_QUERY_GROUP, DATE_KEY_TERM_GROUP,
    DATE_QUERY_YR_GROUP, DATE_QUERY_MTH_GROUP,
    DATE_QUERY_DAY_GROUP, USER_QUERY, YesNo
)

# query terms which only appear in a search
SEARCH_ONLY_QUERIES = [SEARCH_QUERY]
SEARCH_ONLY_QUERIES.extend(DATE_QUERIES)

NON_DATE_QUERIES = [
    USER_QUERY
]
REGEX_MATCHERS = regex_matchers(NON_DATE_QUERIES)
REGEX_MATCHERS.update(regex_date_matchers())

FIELD_LOOKUPS = {
    # query param: filter lookup
    SEARCH_QUERY: '',
    IS_ACTIVE_QUERY: f'{Subscription.IS_ACTIVE_FIELD}',
    # STATUS_QUERY: f'{Opinion.STATUS_FIELD}__{Status.NAME_FIELD}',
    # TITLE_QUERY: f'{Opinion.TITLE_FIELD}__icontains',
    # CONTENT_QUERY: f'{Opinion.CONTENT_FIELD}__icontains',
    # AUTHOR_QUERY: f'{Opinion.USER_FIELD}__{User.USERNAME_FIELD}__icontains',
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
    # else is checked after
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
    if not value:
        return query_set_params

    if query in SEARCH_ONLY_QUERIES:
        query_set_params = get_search_term(
            value, user, query_set_params=query_set_params)
    elif query == IS_ACTIVE_QUERY:
        get_active_query(query_set_params, value)
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
            # if query == CATEGORY_QUERY:
            #     # need inner queryset to get list of categories with names
            #     # like the search term and then look for opinions with those
            #     # categories
            #     get_category_query(query_set_params, match.group(group))
            # elif query == STATUS_QUERY:
            #     # need inner queryset to get list of statuses with names
            #     # like the search term and then look for opinions with those
            #     # statuses
            #     choice_arg_query(
            #         query_set_params, match.group(group).lower(),
            #         QueryStatus, QueryStatus.ALL,
            #         Status, Status.NAME_FIELD, query, FIELD_LOOKUPS[query]
            #     )
            # elif query == HIDDEN_QUERY:
            #     # need to filter/exclude by list of opinions that the user has
            #     # hidden
            #     hidden = Hidden.from_arg(match.group(group).lower())
            #     success = get_hidden_query(query_set_params, hidden, user)
            # elif query == PINNED_QUERY:
            #     # need to filter/exclude by list of opinions that the user has
            #     # pinned
            #     pinned = Pinned.from_arg(match.group(group).lower())
            #     success = get_pinned_query(query_set_params, pinned, user)
            if query in DATE_QUERIES:
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

    # if query_set_params.is_empty and value:
    #     query_set_params.search_type = SearchType.FREE if not any(
    #         list(
    #             map(lambda x: x in value, MARKER_CHARS)
    #         )
    #     ) else SearchType.UNKNOWN
    #
    #     if query_set_params.search_type == SearchType.FREE:
    #         # no delimiting chars, so search title & content for
    #         # any of the search terms
    #         to_query = [TITLE_QUERY, CONTENT_QUERY]
    #         or_q = {}
    #         for term in value.split():
    #             if len(or_q) == 0:
    #                 or_q = {q: [term] for q in to_query}
    #             else:
    #                 or_q[TITLE_QUERY].append(term)
    #                 or_q[CONTENT_QUERY].append(term)
    #
    #         # https://docs.djangoproject.com/en/4.1/topics/db/queries/#complex-lookups-with-q
    #
    #         # OR queries of title and content contains terms
    #         # e.g. [
    #         #   "WHERE ("title") LIKE '<term>'",
    #         #   "WHERE ("content") LIKE '<term>'"
    #         # ]
    #         for qry in to_query:
    #             query_set_params.add_or_lookup(
    #                 '-'.join(to_query),
    #                 Q(_connector=Q.OR, **{
    #                     FIELD_LOOKUPS[qry]: term for term in or_q[qry]
    #                 })
    #             )

    return query_set_params


# def get_category_query(query_set_params: QuerySetParams,
#                        name: str) -> None:
#     """
#     Get the category query
#     :param query_set_params: query params to update
#     :param name: category name or part thereof
#     """
#     # need inner queryset to get list of categories with names
#     # like the search term and then look for opinions with those
#     # categories
#     # https://docs.djangoproject.com/en/4.1/ref/models/querysets/#icontains
#     inner_qs = Category.objects.filter(**{
#         f'{Category.NAME_FIELD}__icontains': name
#     })
#     query_set_params.add_and_lookup(
#         CATEGORY_QUERY, FIELD_LOOKUPS[CATEGORY_QUERY], inner_qs)


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


def get_active_query(query_set_params: QuerySetParams, active: YesNo) -> bool:
    """
    Add an active status query to the query params
    :param query_set_params: params to update
    :param active: active status
    :return: True if successfully added
    """
    if active == YesNo.IGNORE:
        query_set_params.add_all_inclusive(IS_ACTIVE_QUERY)
    else:
        query_set_params.add_and_lookup(
            Subscription.IS_ACTIVE_FIELD, active.boolean)


def subscription_query(action: QueryParam = QueryParam.FILTER) -> QuerySet:
    """
    Get subscriptions
    :param action: query action; default QueryParam.FILTER
    :return: addresses
    """
    params = {}

    if action == QueryParam.FILTER:
        query_set = Subscription.objects.filter(**params)
    elif action == QueryParam.EXCLUDE:
        query_set = Subscription.objects.exclude(**params)
    else:
        raise ValueError(f'Unknown param {action}')
    return query_set


def user_subscription_query(
    user: User, active: bool = True,
    last_expired: bool = False
) -> Tuple[Optional[UserSubscription], Optional[UserSubscription]]:
    """
    Get the specified user's currently active subscription
    :param user: user to search for
    :param active: get active user subscription flag; default True
    :param last_expired: get last expired user subscription flag;
                     default False
    :return: tuple of active/expired subscription
    """
    assert active or last_expired

    # all subscriptions count
    query = UserSubscription.objects.filter(**{
        f'{UserSubscription.USER_FIELD}': user,
    }).order_by(
        UserSubscription.date_lookup(UserSubscription.END_DATE_FIELD)
    )
    count = query.count()

    # precursor to subscription query is check for expired subscriptions
    query.filter(**{
        f'{UserSubscription.END_DATE_FIELD}__lt':
            datetime.now(tz=timezone.utc)
    }).update(**{
        f'{UserSubscription.IS_ACTIVE_FIELD}': False
    })

    active_sub = None
    if active:
        active_user_subs = list(
            query.filter(**{
                UserSubscription.IS_ACTIVE_FIELD: True
            }).all()
        )
        assert len(active_user_subs) <= 1
        if len(active_user_subs) == 1:
            active_sub = active_user_subs[0]

    expired_sub = None
    if last_expired:
        expired_user_subs = list(
            query.filter(**{
                UserSubscription.IS_ACTIVE_FIELD: False
            }).all()
        )
        if len(expired_user_subs) > 0:
            expired_sub = expired_user_subs[-1]

    return active_sub, expired_sub


def user_has_subscription(
    user: User, last_expired: bool = False
) -> Tuple[bool, Optional[UserSubscription], Optional[UserSubscription]]:
    """
    Check if the specified user's has an active user subscription
    :param user: user to search for
    :param last_expired: get last expired user subscription flag;
                     default False
    :return: tuple of active subscription True/False and user subscription
    """
    user_sub, expired_sub = user_subscription_query(
        user, active=True, last_expired=last_expired)
    return (user_sub is not None, user_sub, expired_sub) \
        if not user.is_superuser else (True, None, None)


def get_subscription_features(
        subscription_id: int) -> Optional[List[SubscriptionFeature]]:
    """
    Get the list of subscription features
    :param subscription_id: id of subscription
    :return: list of features or None if subscription not found
    """
    subscription = Subscription.objects.prefetch_related(
        Subscription.FEATURES_FIELD).get(**{
            f'{Subscription.id_field()}': subscription_id
        })
    if subscription:
        features = list(
            filter(lambda f: f.is_active, list(subscription.features.all()))
        )
    else:
        features = None

    return features
