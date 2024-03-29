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
from typing import Any, Optional, Tuple, List, Union
from zoneinfo import ZoneInfo
from decimal import Decimal, InvalidOperation

from django.db.models import QuerySet

from subscription.constants import IS_ACTIVE_QUERY
from subscription.models import (
    Subscription, UserSubscription, SubscriptionFeature, SubscriptionStatus
)
from user.models import User
from utils import (
    SEARCH_QUERY, DATE_QUERIES,
    regex_matchers, regex_date_matchers, QuerySetParams,
    TERM_GROUP, KEY_TERM_GROUP, DATE_QUERY_GROUP, DATE_KEY_TERM_GROUP,
    DATE_QUERY_YR_GROUP, DATE_QUERY_MTH_GROUP,
    DATE_QUERY_DAY_GROUP, USER_QUERY, YesNo, amount_lookups
)
from utils.search import AMOUNT_QUERIES

NON_DATE_QUERIES = [
    USER_QUERY
]
NON_DATE_QUERIES.extend(AMOUNT_QUERIES)
REGEX_MATCHERS = regex_matchers(NON_DATE_QUERIES)
REGEX_MATCHERS.update(regex_date_matchers())

FIELD_LOOKUPS = {
    # query param: filter lookup
    SEARCH_QUERY: '',
    IS_ACTIVE_QUERY: f'{Subscription.IS_ACTIVE_FIELD}',
}
FIELD_LOOKUPS.update(
    amount_lookups(Subscription.AMOUNT_FIELD))
# priority order list of query terms
FILTERS_ORDER = [
    # search is a shortcut filter, if search is specified nothing
    # else is checked after therefore must be first
    SEARCH_QUERY,
]
ALWAYS_FILTERS = [
    # always applied items
]
FILTERS_ORDER.extend(
    [q for q in FIELD_LOOKUPS if q not in FILTERS_ORDER]
)
# complex queries which require more than a simple lookup or context-related
NON_LOOKUP_ARGS = [
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
    elif query == IS_ACTIVE_QUERY:
        get_active_query(query_set_params, value)
    elif query in AMOUNT_QUERIES:
        get_amount_query(
            query_set_params, query, value)
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
            if query in DATE_QUERIES:
                success = get_date_query(query_set_params, query, *[
                    match.group(idx) for idx in [
                        DATE_QUERY_YR_GROUP, DATE_QUERY_MTH_GROUP,
                        DATE_QUERY_DAY_GROUP
                    ]
                ])
            elif query in AMOUNT_QUERIES:
                success = get_amount_query(
                    query_set_params, query, match.group(group))
            elif query not in NON_LOOKUP_ARGS:
                query_set_params.add_and_lookup(
                    query, FIELD_LOOKUPS[query], match.group(group))
            else:
                # complex query term handled elsewhere
                success = False

            save_term_func = query_set_params.add_search_term if success \
                else query_set_params.add_invalid_term
            save_term_func(match.group(key_val_group))

    return query_set_params


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


def get_amount_query(query_set_params: QuerySetParams,
                     query: str, amount: str) -> bool:
    """
    Get an amount query
    :param query_set_params: query params to update
    :param query: query key
    :param amount: amount
    :return: True if successfully added
    """
    success = True
    try:
        amt = Decimal(amount)
        query_set_params.add_and_lookup(
            query, FIELD_LOOKUPS[query], amt)
    except InvalidOperation:
        # ignore invalid amount
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
    expired_val = {
        f'{UserSubscription.STATUS_FIELD}': SubscriptionStatus.EXPIRED.choice
    }
    active_val = {
        f'{UserSubscription.STATUS_FIELD}': SubscriptionStatus.ACTIVE.choice
    }
    eol_val = active_val.copy()
    eol_val[f'{UserSubscription.END_DATE_FIELD}__lt'] = \
        datetime.now(tz=timezone.utc)
    query.filter(**eol_val).update(**expired_val)

    active_sub = None
    if active:
        active_user_subs = list(
            query.filter(**active_val).all()
        )
        assert len(active_user_subs) <= 1
        if len(active_user_subs) == 1:
            active_sub = active_user_subs[0]

    expired_sub = None
    if last_expired:
        expired_user_subs = list(
            query.filter(**expired_val).all()
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


def user_had_free_trial_subscription(user: User) -> bool:
    """
    Check if the specified user has had a free trial subscription
    :param user: user to search for
    :return: True if had free trial
    """
    query = UserSubscription.objects.filter(**{
        f'{UserSubscription.USER_FIELD}': user,
        f'{UserSubscription.SUBSCRIPTION_FIELD}__{Subscription.AMOUNT_FIELD}':
            Decimal(0),
    }).order_by(
        UserSubscription.date_lookup(UserSubscription.END_DATE_FIELD)
    )
    count = query.count()

    return count > 0


def user_subscription_features(
        user: User) -> Tuple[Optional[List[SubscriptionFeature]], datetime]:
    """
    Check if the specified user's has an active user subscription
    :param user: user to search for
    :return: tuple of list of subscription feature and subscription start
    """
    _, user_sub, _ = user_has_subscription(user)

    return (get_subscription_features(user_sub.subscription),
            user_sub.start_date) if user_sub else (None, None)


def get_subscription_features(subscription_id: Union[int, Subscription]
                              ) -> Optional[List[SubscriptionFeature]]:
    """
    Get the list of subscription features
    :param subscription_id: id of subscription
    :return: list of features or None if subscription not found
    """
    subscription = Subscription.objects.prefetch_related(
        Subscription.FEATURES_FIELD).get(**{
            f'{Subscription.id_field()}': subscription_id.id
            if isinstance(subscription_id, Subscription) else subscription_id
        })
    if subscription:
        features = list(
            filter(lambda f: f.is_active, list(subscription.features.all()))
        )
    else:
        features = None

    return features
