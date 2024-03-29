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
from enum import Enum
from typing import Type, Callable, Tuple, Optional, List
from string import capwords
from decimal import Decimal

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest
from django.contrib import messages

from base.utils import raise_permission_denied
from utils import (
    QueryArg, SortOrder, QuerySetParams, QueryOption, ContentListMixin,
    TITLE_CTX, LIST_HEADING_CTX, PAGE_HEADING_CTX, NO_CONTENT_MSG_CTX,
    Crud, app_template_path, ORDER_QUERY, PAGE_QUERY, PER_PAGE_QUERY, PerPage6,
    REORDER_QUERY, REORDER_REQ_QUERY_ARGS, YesNo,
    READ_ONLY_CTX, AMOUNT_QUERY_ARGS, REPEAT_SEARCH_TERM_CTX, query_search_term
)
from utils.search import AMT_GT_QUERY, SEARCH_QUERY

from .utils import (
    subscription_permission_check
)
from subscription.subscription_queries import (
    get_lookup, user_has_subscription, user_had_free_trial_subscription,
    FILTERS_ORDER, ALWAYS_FILTERS
)
from subscription.constants import (
    THIS_APP, SUBSCRIPTION_LIST_CTX, IS_ACTIVE_QUERY
)
from subscription.views.dto import SubscriptionDto
from ..enums import SubscriptionSortOrder, SubscriptionQueryType
from ..models import Subscription


# args for an address reorder/next page/etc. request
REORDER_QUERY_ARGS = [
    QueryOption(
        ORDER_QUERY, SubscriptionSortOrder, SubscriptionSortOrder.DEFAULT),
    QueryOption.of_no_cls(PAGE_QUERY, 1),
    QueryOption(PER_PAGE_QUERY, PerPage6, PerPage6.DEFAULT),
    QueryOption.of_no_cls(REORDER_QUERY, 0),
]
assert REORDER_REQ_QUERY_ARGS == list(
    map(lambda query_opt: query_opt.query, REORDER_QUERY_ARGS)
)

# request arguments for a subscription list request
LIST_QUERY_ARGS = REORDER_QUERY_ARGS.copy()
LIST_QUERY_ARGS.extend([
    # non-reorder query args
    QueryOption.of_no_cls_dflt(SEARCH_QUERY),
    QueryOption(IS_ACTIVE_QUERY, YesNo, YesNo.DEFAULT)
])
LIST_QUERY_ARGS.extend(AMOUNT_QUERY_ARGS)


ADD_NEW = 'add_new'


class ListTemplate(Enum):
    """ Enum representing possible response template """
    FULL_TEMPLATE = app_template_path(THIS_APP, 'subscription_list.html')
    """ Whole page template """
    CONTENT_TEMPLATE = app_template_path(
        THIS_APP, 'subscription_list_content.html')
    """ List-only template for requery """
    CHOICE_TEMPLATE = app_template_path(THIS_APP, 'select_subscription.html')
    """ Choose subscription page template """


class SubscriptionList(LoginRequiredMixin, ContentListMixin):
    """
    Subscription list response
    """
    # inherited from MultipleObjectMixin via ListView
    model = Subscription

    def __init__(self):
        super().__init__()
        # response template to use
        self.response_template = ListTemplate.FULL_TEMPLATE

        self.initialise()

    def permission_check_func(
            self) -> Callable[[HttpRequest, Crud, bool], bool]:
        """
        Get the permission check function
        :return: permission check function
        """
        return subscription_permission_check

    def valid_req_query_args(self) -> List[QueryOption]:
        """
        Get the valid request query args
        :return: dict of query args
        """
        return LIST_QUERY_ARGS

    def additional_check_func(
            self, request: HttpRequest, query_params: dict[str, QueryArg],
            *args, **kwargs):
        """
        Perform additional access checks.
        :param request: http request
        :param query_params: request query
        :param args: additional arbitrary arguments
        :param kwargs: additional keyword arguments
        """
        active = request.user.is_active
        is_super = request.user.is_superuser
        if not (active or is_super):
            raise_permission_denied(request, Subscription, plural='s')

    def validate_queryset(self, query_params: dict[str, QueryArg]):
        """
        Validate the query params to get the list of items for this view.
        (Subclasses may validate and modify the query params by overriding
         this function)
        :param query_params: request query
        """
        self.query_type = SubscriptionQueryType.UNKNOWN
        if not self.query_param_was_set(query_params):
            # no query params, basic all subscriptions query
            self.query_type = SubscriptionQueryType.ALL_SUBSCRIPTIONS

    def set_extra_context(self, query_params: dict[str, QueryArg],
                          query_set_params: QuerySetParams):
        """
        Set the context extra content to be added to context
        :param query_params: request query
        :param query_set_params: QuerySetParams
        """
        # build search term string from values that were set
        # inherited from ContextMixin via ListView
        self.extra_context = {
            REPEAT_SEARCH_TERM_CTX: query_search_term(
                query_params, exclude_queries=REORDER_REQ_QUERY_ARGS)
        }

        self.extra_context.update(
            self.get_title_heading(query_params))

    def get_title_heading(self, query_params: dict[str, QueryArg]) -> dict:
        """
        Get the title and page heading for context
        :param query_params: request query
        """
        title = 'Subscriptions'

        return {
            TITLE_CTX: title,
            LIST_HEADING_CTX: capwords(title),
            READ_ONLY_CTX: False
        }

    def set_queryset(
        self, query_params: dict[str, QueryArg],
        query_set_params: QuerySetParams = None
    ) -> Tuple[QuerySetParams, bool, Optional[dict]]:
        """
        Set the queryset to get the list of items for this view
        :param query_params: request query
        :param query_set_params: QuerySetParams to update; default None
        :return: tuple of query set params, query term entered flag and
                dict of kwargs to pass to `apply_queryset_param()`
        """
        if query_set_params is None:
            query_set_params = QuerySetParams()

        query_entered = False  # query term entered flag

        for key in FILTERS_ORDER:
            value, was_set = query_params[key].as_tuple

            if value is not None:
                if key in ALWAYS_FILTERS and not was_set:
                    # don't set always applied filter until everything
                    # else is checked
                    continue

                if not query_entered:
                    query_entered = was_set

                get_lookup(
                    key, value, self.user, query_set_params=query_set_params)

                if key == SEARCH_QUERY and not query_set_params.is_empty:
                    # search is a shortcut filter, if search is specified
                    # nothing else is checked after
                    break

        return query_set_params, query_entered, None

    def apply_queryset_param(self, query_params: dict[str, QueryArg],
                             query_set_params: QuerySetParams,
                             query_entered: bool, **kwargs):
        """
        Apply `query_set_params` to set the queryset
        :param query_params: request query
        :param query_set_params: QuerySetParams to apply
        :param query_entered: query was entered flag
        """
        if not query_entered or not query_set_params.is_empty:
            # no query term entered => all objects,
            # or query term => search

            for key in ALWAYS_FILTERS:
                if query_set_params.key_in_set(key):
                    continue    # always filter was already applied

                value = query_params[key].value
                if value:
                    get_lookup(key, value, self.user,
                               query_set_params=query_set_params)

            self.queryset = query_set_params.apply(Subscription.objects)

        else:
            # invalid query term entered
            self.queryset = Subscription.objects.none()

    def set_sort_order_options(self, query_params: dict[str, QueryArg]):
        """
        Set the sort order options for the response
        :param query_params: request query
        :return:
        """
        # select sort order options to display
        excludes = []
        self.sort_order = [
            so for so in SubscriptionSortOrder if so not in excludes
        ]

    def get_sort_order_enum(self) -> Type[SortOrder]:
        """
        Get the subclass-specific SortOrder enum
        :return: SortOrder enum
        """
        return SubscriptionSortOrder

    def select_template(
            self, query_params: dict[str, QueryArg]):
        """
        Select the template for the response
        :param query_params: request query
        """
        reorder_query = self.is_reorder(query_params)
        self.response_template = ListTemplate.CONTENT_TEMPLATE \
            if reorder_query else ListTemplate.FULL_TEMPLATE

        # inherited from TemplateResponseMixin via ListView
        self.template_name = self.response_template.value

    def get_context_data(self, *, object_list=None, **kwargs) -> dict:
        """
        Get template context
        :param object_list:
        :param kwargs: additional keyword arguments;
                add_new: add new entity placeholder flag
        :return: context
        """
        context = super().get_context_data(object_list=object_list, **kwargs)

        self.context_std_elements(context=context)

        if len(context[SUBSCRIPTION_LIST_CTX]) == 0:
            # move list heading to page heading as no content
            context[PAGE_HEADING_CTX] = context[LIST_HEADING_CTX]
            del context[LIST_HEADING_CTX]

        dto_list = [SubscriptionDto.add_new_obj()] \
            if kwargs.get(ADD_NEW, True) else []
        dto_list.extend([
            SubscriptionDto.from_model(subscription)
            for subscription in context[SUBSCRIPTION_LIST_CTX]
        ])
        context[SUBSCRIPTION_LIST_CTX] = dto_list

        return self.add_no_content_context(context)

    def add_no_content_context(self, context: dict) -> dict:
        """
        Add no content-specific info to context
        :param context: context
        :return: context
        """
        if len(context[SUBSCRIPTION_LIST_CTX]) == 0:
            context[NO_CONTENT_MSG_CTX] = 'No subscriptions found.'

        return context

    def is_list_only_template(self) -> bool:
        """
        Is the current render template, the list only template
        :return: True if the list only template
        """
        return self.response_template == ListTemplate.CONTENT_TEMPLATE


class SubscriptionChoice(SubscriptionList):
    """
    Subscription choices list response
    """

    def __init__(self):
        super().__init__()

        self.has_subscription = False

    def validate_queryset(self, query_params: dict[str, QueryArg]):
        """
        Validate the query params to get the list of items for this view.
        (Subclasses may validate and modify the query params by overriding
         this function)
        :param query_params: request query
        """
        super().validate_queryset(query_params)

        # check if user has had free trial
        if user_had_free_trial_subscription(self.user):
            query_params[AMT_GT_QUERY] = QueryArg(Decimal(0), True)

    def additional_check_func(
            self, request: HttpRequest, query_params: dict[str, QueryArg],
            *args, **kwargs):
        """
        Perform additional access checks.
        :param request: http request
        :param query_params: request query
        :param args: additional arbitrary arguments
        :param kwargs: additional keyword arguments
        """
        super().additional_check_func(request, query_params, *args, **kwargs)

        has_sub, user_sub, _ = user_has_subscription(request.user)
        if has_sub:
            sub_type = 'trial' if user_sub.is_free_trial else 'current'
            msg = f'Your {sub_type} subscription is ' \
                  f'{user_sub.subscription.name}, ' \
                  f'expiring {user_sub.end_date.strftime("%c")}'
            messages.add_message(request, messages.INFO, msg)
        self.has_subscription = has_sub

    def select_template(self, query_params: dict[str, QueryArg]):
        """
        Select the template for the response
        :param query_params: request query
        """
        self.response_template = ListTemplate.CHOICE_TEMPLATE
        self.template_name = self.response_template.value

    def get_title_heading(self, query_params: dict[str, QueryArg]) -> dict:
        """
        Get the title and page heading for context
        :param query_params: request query
        """
        title = 'Subscription Choice'

        return {
            TITLE_CTX: title,
            PAGE_HEADING_CTX: title,
            LIST_HEADING_CTX: capwords(title),
            READ_ONLY_CTX: self.has_subscription
        }

    def get_context_data(self, *, object_list=None, **kwargs) -> dict:
        """
        Get template context
        :param object_list:
        :param kwargs: additional keyword arguments;
                add_new: add new entity placeholder flag
        :return: context
        """
        ctx_kwargs = kwargs.copy()
        ctx_kwargs[ADD_NEW] = False
        return super().get_context_data(
            object_list=object_list, **ctx_kwargs)

    def set_ordering(self, query_params: dict[str, QueryArg]):
        """
        Set the ordering for the response
        :param query_params: request query
        """
        # set ordering
        self.ordering = SubscriptionSortOrder.COST_LH.order,
