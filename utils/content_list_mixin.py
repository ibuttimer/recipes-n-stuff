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
from datetime import datetime
from http import HTTPStatus
from typing import Type, Callable, Tuple, Optional, List, Any, Union

from django.core.paginator import Paginator
from django.db.models.functions import Lower
from django.http import HttpRequest, HttpResponse
from django.template.loader import render_to_string
from django.views import generic

from .search import (
    ORDER_QUERY, PER_PAGE_QUERY, REORDER_QUERY, USER_QUERY,
    REORDER_REQ_QUERY_ARGS
)
# from user.models import User
# from django.contrib.auth.models import AbstractUser

from .misc import Crud
from .models import DESC_LOOKUP
from .query_params import QuerySetParams
from .enums import (
    QueryOption, QueryArg, SortOrder, PerPage6, ChoiceArg, PerPageMixin
)

# general context keys
TITLE_CTX = 'title'                             # page title
PAGE_HEADING_CTX = 'page_heading'               # page heading display
LIST_HEADING_CTX = 'list_heading'               # list heading display
LIST_SUB_HEADING_CTX = 'list_sub_heading'       # list sub heading display
REPEAT_SEARCH_TERM_CTX = 'repeat_search_term'   # search term for query
NO_CONTENT_MSG_CTX = 'no_content_msg'           # no content message
NO_CONTENT_HELP_CTX = 'no_content_help'         # help text when no content
READ_ONLY_CTX = 'read_only'                     # read-only mode
SUBMIT_URL_CTX = 'submit_url'
SUBMIT_BTN_TEXT_CTX = 'submit_btn_text'
SNIPPETS_CTX = 'snippets'

SORT_ORDER_CTX = 'sort_order'
SELECTED_SORT_CTX = 'selected_sort'
PER_PAGE_CTX = 'per_page'
SELECTED_PER_PAGE_CTX = 'selected_per_page'
PAGE_LINKS_CTX = 'page_links'
PAGE_NUM_CTX = 'page_num'
DISABLED_CTX = 'disabled'
HREF_CTX = 'href'
LABEL_CTX = 'label'
HIDDEN_CTX = 'hidden'
STATUS_CTX = 'status'

# from django.views.generic.list.MultipleObjectMixin
PAGINATOR_CTX = 'paginator'
PAGE_OBJ_CTX = 'page_obj'

OPINION_PAGINATION_ON_EACH_SIDE = 1
OPINION_PAGINATION_ON_ENDS = 1


class ContentListMixin(generic.ListView):
    """ Mixin for content list views """

    # sort order options to display
    sort_order: Type[SortOrder]
    # user which initiated request
    user: Any
    # query args sent for list request which are not always sent with
    # a reorder request
    non_reorder_query_args = List[str]
    # query type
    query_type: Any
    sub_query_type: Any

    def __init__(self):
        self.sort_order = None
        self.user = None
        # query args sent for list request which are not always sent with
        # a reorder request
        self.non_reorder_query_args = None
        # query type
        self.query_type = None
        self.sub_query_type = None

    def initialise(self, non_reorder_args: List[str] = None):
        """
        Initialise this instance
        (The method resolution order is too extended to use a simple
         super().__init__(). See
         https://docs.python.org/3.10/library/functions.html#super)
        """
        self.non_reorder_query_args = [
            a.query for a in self.valid_req_query_args()
            if a.query not in REORDER_REQ_QUERY_ARGS
        ] if non_reorder_args is None else non_reorder_args

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """
        GET method for Opinion list
        :param request: http request
        :param args: additional arbitrary arguments
        :param kwargs: additional keyword arguments
        :return: http response
        """
        self.permission_check_func()(request, Crud.READ)

        self.user = request.user

        # TODO currently '/"/= can't be used in content
        # as search depends on them
        query_params = self.req_query_args()(request)
        self.validate_queryset(query_params)

        self.additional_check_func(
            request, query_params, args=args, kwargs=kwargs)

        # set queryset
        query_set_params, query_entered, query_kwargs = \
            self.set_queryset(query_params)
        self.apply_queryset_param(
            query_params, query_set_params, query_entered,
            **(query_kwargs or {}))

        # set context extra content
        self.set_extra_context(query_params, query_set_params)

        # select sort order options to display
        self.set_sort_order_options(query_params)

        # set ordering
        self.set_ordering(query_params)

        # set pagination
        self.set_pagination(query_params)

        # set template
        self.select_template(query_params)

        return super().get(request, *args, **kwargs)

    def permission_check_func(
            self) -> Callable[[HttpRequest, Crud, bool], bool]:
        """
        Get the permission check function
        :return: permission check function
        """
        raise NotImplementedError(
            "'permission_check_func' method must be overridden by subclasses")

    def additional_check_func(
            self, request: HttpRequest, query_params: dict[str, QueryArg],
            *args, **kwargs):
        """
        Perform additional access checks.
        (Subclasses should override this method to perform additional access
         checks as required)
        :param request: http request
        :param query_params: request query
        :param args: additional arbitrary arguments
        :param kwargs: additional keyword arguments
        """

    def req_query_args(
            self) -> Callable[[HttpRequest], dict[str, QueryArg]]:
        """
        Get the request query args function
        :return: request query args function
        """
        return lambda request: get_query_args(
            request, self.valid_req_query_args())

    def valid_req_query_args(self) -> List[QueryOption]:
        """
        Get the valid request query args
        :return: dict of query args
        """
        raise NotImplementedError(
            "'valid_req_query_args' method must be overridden by subclasses")

    def valid_req_non_reorder_query_args(self) -> List[str]:
        """
        Get the valid request query args
        :return: dict of query args
        """
        return self.non_reorder_query_args

    def validate_queryset(self, query_params: dict[str, QueryArg]):
        """
        Validate the query params to get the list of items for this view.
        (Subclasses may validate and modify the query params by overriding
         this function)
        :param query_params: request query
        """

    def set_extra_context(self, query_params: dict[str, QueryArg],
                          query_set_params: QuerySetParams):
        """
        Set the context extra content to be added to context
        :param query_params: request query
        :param query_set_params: QuerySetParams
        """
        raise NotImplementedError(
            "'set_extra_content' method must be overridden by sub classes")

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
        raise NotImplementedError(
            "'set_queryset' method must be overridden by sub classes")

    def apply_queryset_param(self, query_params: dict[str, QueryArg],
                             query_set_params: QuerySetParams,
                             query_entered: bool, **kwargs):
        """
        Apply `query_set_params` to set the queryset
        :param query_params: request query
        :param query_set_params: QuerySetParams to apply
        :param query_entered: query was entered flag
        """
        raise NotImplementedError(
            "'apply_queryset_param' method must be overridden by sub classes")

    def set_sort_order_options(self, query_params: dict[str, QueryArg]):
        """
        Set the sort order options for the response
        :param query_params: request query
        """
        raise NotImplementedError(
            "'set_sort_order_options' method must be overridden by sub "
            "classes")

    def set_ordering(self, query_params: dict[str, QueryArg]):
        """
        Set the ordering for the response
        :param query_params: request query
        """
        sort_order = self.get_sort_order_enum()

        # set ordering
        order = query_params[ORDER_QUERY].value
        ordering = [order.order]    # list of lookups
        if order.to_field() != sort_order.DEFAULT.to_field():
            # add secondary sort by default sort option
            ordering.append(sort_order.DEFAULT.order)
        # published date is only set once comment is published so apply an
        # additional orderings: by updated and id

        # ordering.append(f'{DATE_NEWEST_LOOKUP}{UPDATED_FIELD}')

        ordering.append(f'{self.model.id_field()}')
        # inherited from MultipleObjectMixin via ListView
        self.ordering = tuple(ordering)

    def get_sort_order_enum(self) -> Type[SortOrder]:
        """
        Get the subclass-specific SortOrder enum
        :return: SortOrder enum
        """
        raise NotImplementedError(
            "'get_sort_order_enum' method must be overridden by sub classes")

    def get_per_page_enum(self) -> Type[ChoiceArg]:
        """
        Get the subclass-specific PerPage enum
        :return: PerPage enum
        """
        return PerPage6

    def set_pagination(
            self, query_params: dict[str, QueryArg]):
        """
        Set pagination for the response
        :param query_params: request query
        """
        # set pagination
        # inherited from MultipleObjectMixin via ListView
        per_page = query_params[PER_PAGE_QUERY]
        self.paginate_by = None \
            if isinstance(per_page, PerPageMixin) and per_page.is_all else \
            query_params[PER_PAGE_QUERY].value_arg_or_value

    def get_ordering(self):
        """ Get ordering of list """
        ordering = self.ordering
        if isinstance(ordering, tuple):
            # make primary sort case-insensitive
            # https://docs.djangoproject.com/en/4.1/ref/models/querysets/#django.db.models.query.QuerySet.order_by
            def insensitive_order(order: str):
                """ Make text orderings case-insensitive """
                return \
                    order if self.model.is_non_text_lookup(order) else \
                    Lower(order[1:]).desc() \
                    if order.startswith(DESC_LOOKUP) else Lower(order)
            ordering = tuple(
                map(insensitive_order, ordering))
        return ordering

    def context_std_elements(self, context: dict) -> dict:
        """
        Update the specified context with the standard elements:
        - sort order
        - per page
        - pagination
        :param context: context to update
        :return: context
        """
        # initial ordering if secondary sort
        main_order = self.ordering \
            if isinstance(self.ordering, str) else self.ordering[0]
        context.update({
            SORT_ORDER_CTX: self.sort_order,
            SELECTED_SORT_CTX: list(
                filter(lambda order: order.order == main_order,
                       self.get_sort_order_enum())
            )[0],
            PER_PAGE_CTX: list(self.get_per_page_enum()),
            SELECTED_PER_PAGE_CTX: self.paginate_by,
            PAGE_LINKS_CTX: [{
                PAGE_NUM_CTX: page,
                DISABLED_CTX: page == Paginator.ELLIPSIS,
                HREF_CTX:
                    f"?page={page}" if page != Paginator.ELLIPSIS else '#',
                LABEL_CTX:
                    f"page {page}" if page != Paginator.ELLIPSIS else '',
                HIDDEN_CTX: f'{str(bool(page != Paginator.ELLIPSIS)).lower()}',
            } for page in context[PAGINATOR_CTX].get_elided_page_range(
                number=context[PAGE_OBJ_CTX].number,
                on_each_side=OPINION_PAGINATION_ON_EACH_SIDE,
                on_ends=OPINION_PAGINATION_ON_ENDS)
            ]
        })
        return context

    @staticmethod
    def has_no_content(context: dict, key: str = "object_list") -> bool:
        """
        Check if response has no content
        :param context: response context
        :param key: object list key in context; default "object_list"
        :return: True if no content
        """
        return len(context[key]) == 0

    @staticmethod
    def render_no_content_help(
            context: dict, template: str, template_ctx: dict = None) -> dict:
        """
        Add no content-specific help to context
        :param context: context
        :param template: template path
        :param template_ctx: template context
        :return: context
        """
        if template:
            context[NO_CONTENT_HELP_CTX] = render_to_string(
                template, context=template_ctx)
        return context

    def select_template(self, query_params: dict[str, QueryArg]):
        """
        Select the template for the response
        :param query_params: request query
        """
        raise NotImplementedError(
            "'select_template' method must be overridden by sub classes")

    def render_to_response(self, context, **response_kwargs):
        """
        Return a response, using the `response_class` for this view, with a
        template rendered with the given context.

        Pass response_kwargs to the constructor of the response class.
        """
        # return 204 for no content
        if self.is_list_only_template() and len(context['object_list']) == 0:
            response_kwargs['status'] = HTTPStatus.NO_CONTENT

        return super().render_to_response(context, **response_kwargs)

    def is_list_only_template(self) -> bool:
        """
        Is the current render template, the list only template
        :return: True if the list only template
        """
        raise NotImplementedError(
            "'is_list_only_template' method must be overridden by sub "
            "classes")

    @staticmethod
    def query_value_was_set_as_value(
            query_params: dict[str, QueryArg], query: str,
            value: Any) -> bool:
        """
        Check if the specified query was set to the specified value
        :param query_params: query params
        :param query: query to check
        :param value: value to check
        :return: True if query was set to the specified value
        """
        query_arg = query_params.get(query, None)
        return query_arg is not None and query_arg.was_set_to(value)

    @staticmethod
    def query_value_was_set(
            query_params: dict[str, QueryArg], query: str) -> bool:
        """
        Check if the specified query was set
        :param query_params: query params
        :param query: query to check
        :return: True if query was set to the specified value
        """
        query_arg = query_params.get(query, None)
        return query_arg is not None and query_arg.was_set

    @staticmethod
    def query_value_was_set_as_one_of_values(
            query_params: dict[str, QueryArg], query: str,
            values: List[Any]) -> bool:
        """
        Check if the specified query was set to one of the specified values
        :param query_params: query params
        :param query: query to check
        :param values: values to check
        :return: True if query was set to one of the specified values
        """
        query_arg = query_params.get(query, None)
        return query_arg is not None and query_arg.was_set_to_one_of(values)

    def is_query_own(self, query_params: dict[str, QueryArg]) -> bool:
        """
        Check if query is for the current user
        :param query_params: query params
        :return: True is current user is author in query
        """
        return self.query_value_was_set_as_value(
            query_params, USER_QUERY, self.user.username)

    @staticmethod
    def query_param_was_set(query_params: dict[str, QueryArg]) -> bool:
        """
        Check if any query params were set
        :param query_params: query params
        :return: True at least 1 query param was set
        """
        for query, query_arg in query_params.items():
            was_set = isinstance(query_arg, QueryArg) and query_arg.was_set
            if was_set:
                break
        else:
            was_set = False
        return was_set

    def get_since(
            self, query_params: dict[str, QueryArg]) -> Optional[datetime]:
        """
        Get the query since date
        :param query_params: request query
        :return: since date or None
        """
        return None
        # if \
        # query_params.get(FILTER_QUERY, FilterMode.DEFAULT).value == \
        # FilterMode.ALL else self.user.previous_login

    @staticmethod
    def is_reorder(query_params: dict[str, QueryArg]):
        """ Check if request is a reorder request """
        return query_params[REORDER_QUERY].value \
            if REORDER_QUERY in query_params else False


def get_query_args(
        request: HttpRequest,
        options: Union[QueryOption, List[QueryOption]]
) -> dict[str, QueryArg]:
    """
    Get opinion list query arguments from request query
    :param request: http request
    :param options: list of possible QueryOption
    :return: dict of key query and value (QueryArg | int | str)
    """
    # https://docs.djangoproject.com/en/4.1/ref/request-response/#querydict-objects
    params = {}
    if isinstance(options, QueryOption):
        options = [options]

    for option in options:
        params[option.query] = QueryArg.of(option.default)

        if option.query in request.GET:
            param = request.GET[option.query].lower()

            default_value = params[option.query].value_arg_or_value
            if isinstance(default_value, int):
                param = int(param)  # default is int so param should be too

            if option.clazz:
                choice = list(
                    map(option.clazz.from_arg, param.split())
                ) if isinstance(param, str) and ' ' in param else \
                    option.clazz.from_arg(param)

                params[option.query].set(choice, True)
            else:
                params[option.query].set(param, True)

    return params
