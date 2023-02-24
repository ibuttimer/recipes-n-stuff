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

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import F
from django.http import HttpRequest
from django.template.loader import render_to_string
from django.contrib import messages

from base.utils import raise_permission_denied
from base.views import MESSAGE_CTX
from utils import (
    QueryArg, SortOrder, QuerySetParams, QueryOption, ContentListMixin,
    TITLE_CTX, LIST_HEADING_CTX, PAGE_HEADING_CTX, NO_CONTENT_MSG_CTX,
    NO_CONTENT_HELP_CTX,
    Crud, app_template_path, ORDER_QUERY, PAGE_QUERY, PER_PAGE_QUERY, PerPage8,
    REORDER_QUERY, REORDER_REQ_QUERY_ARGS, YesNo,
    READ_ONLY_CTX, AMOUNT_QUERY_ARGS, REPEAT_SEARCH_TERM_CTX, query_search_term,
    LIST_SUB_HEADING_CTX, ChoiceArg
)
from utils.content_list_mixin import SELECTED_SORT_CTX
from utils.search import SEARCH_QUERY

from recipes.constants import (
    THIS_APP, RECIPE_LIST_CTX, AUTHOR_QUERY, KEYWORD_QUERY, TIME_CTX
)
from recipes.views.utils import (
    recipe_permission_check
)
from recipes.views.recipe_queries import (
    get_lookup, FILTERS_ORDER, ALWAYS_FILTERS
)
from .dto import RecipeDto
from ..enums import RecipeSortOrder, RecipeQueryType
from ..models import Recipe


# args for an address reorder/next page/etc. request
REORDER_QUERY_ARGS = [
    QueryOption(
        ORDER_QUERY, RecipeSortOrder, RecipeSortOrder.DEFAULT),
    QueryOption.of_no_cls(PAGE_QUERY, 1),
    QueryOption(PER_PAGE_QUERY, PerPage8, PerPage8.DEFAULT),
    QueryOption.of_no_cls(REORDER_QUERY, 0),
]
assert REORDER_REQ_QUERY_ARGS == list(
    map(lambda query_opt: query_opt.query, REORDER_QUERY_ARGS)
)

# request arguments for a recipe list request
LIST_QUERY_ARGS = REORDER_QUERY_ARGS.copy()
LIST_QUERY_ARGS.extend([
    # non-reorder query args
    QueryOption.of_no_cls_dflt(SEARCH_QUERY),
    QueryOption.of_no_cls_dflt(KEYWORD_QUERY),
])
# request arguments for an opinion search request
SEARCH_QUERY_ARGS = LIST_QUERY_ARGS.copy()
SEARCH_QUERY_ARGS.extend([
    QueryOption.of_no_cls_dflt(query) for query in [
        AUTHOR_QUERY
    ]
])
# LIST_QUERY_ARGS.extend(OPINION_APPLIED_DEFAULTS_QUERY_ARGS)


class ListTemplate(Enum):
    """ Enum representing possible response template """
    FULL_TEMPLATE = app_template_path(THIS_APP, 'recipe_list.html')
    """ Whole page template """
    CONTENT_TEMPLATE = app_template_path(
        THIS_APP, 'recipe_list_content.html')
    """ List-only template for requery """


class RecipeList(LoginRequiredMixin, ContentListMixin):
    """
    Class-based view for recipe list
    """
    # inherited from MultipleObjectMixin via ListView
    model = Recipe

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
        return recipe_permission_check

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
            raise_permission_denied(request, Recipe, plural='s')

    def validate_queryset(self, query_params: dict[str, QueryArg]):
        """
        Validate the query params to get the list of items for this view.
        (Subclasses may validate and modify the query params by overriding
         this function)
        :param query_params: request query
        """
        self.query_type = RecipeQueryType.UNKNOWN
        if not self.query_param_was_set(query_params):
            # no query params, basic all recipes query
            self.query_type = RecipeQueryType.ALL_RECIPES

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
        title = 'Recipes'

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

        if self.query_value_was_set_as_one_of_values(
                query_params, ORDER_QUERY, [
                    RecipeSortOrder.TOTAL_TIME_LH,
                    RecipeSortOrder.TOTAL_TIME_HL
                ]):
            # add total time annotation as needed for ordering
            query_set_params.add_annotation(
                ORDER_QUERY, Recipe.TOTAL_TIME_FIELD,
                F(Recipe.PREP_TIME_FIELD) + F(Recipe.COOK_TIME_FIELD)
            )

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

            self.queryset = query_set_params.apply(Recipe.objects)

        else:
            # invalid query term entered
            self.queryset = Recipe.objects.none()

    def set_sort_order_options(self, query_params: dict[str, QueryArg]):
        """
        Set the sort order options for the response
        :param query_params: request query
        :return:
        """
        # select sort order options to display
        self.sort_order = [
            so for so in RecipeSortOrder
        ]

    def get_sort_order_enum(self) -> Type[SortOrder]:
        """
        Get the subclass-specific SortOrder enum
        :return: SortOrder enum
        """
        return RecipeSortOrder

    def get_per_page_enum(self) -> Type[ChoiceArg]:
        """
        Get the subclass-specific PerPage enum
        :return: PerPage enum
        """
        return PerPage8

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

        if self.has_no_content(context):
            # move list heading to page heading as no content
            context[PAGE_HEADING_CTX] = context[LIST_HEADING_CTX]
            del context[LIST_HEADING_CTX]

        dto_list = [
            RecipeDto.from_model(recipe)
            for recipe in context[RECIPE_LIST_CTX]
        ]
        context[RECIPE_LIST_CTX] = dto_list

        context[TIME_CTX] = 'prep' if context[SELECTED_SORT_CTX] in [
            RecipeSortOrder.PREP_TIME_LH, RecipeSortOrder.PREP_TIME_HL
        ] else 'cook' if context[SELECTED_SORT_CTX] in [
            RecipeSortOrder.COOK_TIME_LH, RecipeSortOrder.COOK_TIME_HL,
        ] else 'total'

        return self.add_no_content_context(context)

    def add_no_content_context(self, context: dict) -> dict:
        """
        Add no content-specific info to context
        :param context: context
        :return: context
        """
        if self.has_no_content(context):
            context[NO_CONTENT_MSG_CTX] = 'No recipes found.'

            template = None
            template_ctx = None
            if self.query_type == RecipeQueryType.ALL_RECIPES:
                template = "all_recipes_no_content_msg.html"
            # elif self.query_type == QueryType.ALL_USERS_OPINIONS:
            #     template = "my_opinions_no_content_msg.html"
            # elif self.query_type == QueryType.DRAFT_OPINIONS:
            #     template = "draft_opinions_no_content_msg.html"
            # elif self.query_type == QueryType.PREVIEW_OPINIONS:
            #     template = "preview_opinions_no_content_msg.html"
            #     template_ctx = {
            #         USER_CTX: self.user
            #     }
            # elif self.query_type == QueryType.PINNED_OPINIONS:
            #     template = "pinned_no_content.html"

            self.render_no_content_help(
                context, template, template_ctx=template_ctx)

        return context

    @staticmethod
    def render_no_content_help(
            context: dict, template: str, template_ctx: dict = None) -> dict:
        """
        Add no content-specific help to context
        :param context: context
        :param template: template filename
        :param template_ctx: template context
        :return: context
        """
        if template:
            context[NO_CONTENT_HELP_CTX] = render_to_string(
                app_template_path(
                    THIS_APP, "messages", template),
                context=template_ctx)
        return context

    def is_list_only_template(self) -> bool:
        """
        Is the current render template, the list only template
        :return: True if the list only template
        """
        return self.response_template == ListTemplate.CONTENT_TEMPLATE


class SearchRecipeList(RecipeList):
    """
    Class-based view for recipe search
    """

    def valid_req_query_args(self) -> List[QueryOption]:
        """
        Get the valid request query args
        :return: dict of query args
        """
        return SEARCH_QUERY_ARGS

    def set_sort_order_options(self, query_params: dict[str, QueryArg]):
        """
        Set the sort order options for the response
        :param query_params: request query
        :return:
        """
        # select sort order options to display
        excludes = []
        if query_params[AUTHOR_QUERY].was_set_to(self.user.username):
            # no need for sort by author if only one author
            excludes.extend([
                RecipeSortOrder.AUTHOR_AZ,RecipeSortOrder.AUTHOR_ZA
            ])
        self.sort_order = [
            so for so in RecipeSortOrder if so not in excludes
        ]

    def set_extra_context(self, query_params: dict[str, QueryArg],
                          query_set_params: QuerySetParams):
        """
        Set the context extra content to be added to context
        :param query_params: request query
        :param query_set_params: QuerySetParams
        """
        # build search term string from values that were set

        if query_set_params.is_free_search:
            search_term = query_params[SEARCH_QUERY].value
        else:
            # build search term string from used terms
            search_term = ', '.join(query_set_params.search_terms)

        # string of invalid terms
        invalid_terms = None if not query_set_params.invalid_terms else \
            ', '.join(query_set_params.invalid_terms)

        if query_set_params.is_unknown_search:
            if not search_term:
                search_term = query_params[SEARCH_QUERY].value

        if not invalid_terms and not query_set_params.is_free_search:
            # remove valid terms to leave only invalid terms
            invalid_terms = query_params[SEARCH_QUERY].value
            for term in query_set_params.search_terms:
                invalid_terms = invalid_terms.replace(term, '')
            invalid_terms = invalid_terms.strip()

        if invalid_terms:
            invalid_terms = render_to_string(
                app_template_path(
                    THIS_APP, "messages", "invalid_search_terms_msg.html"),
                context={
                    MESSAGE_CTX: invalid_terms,
                })

        self.extra_context = {
            TITLE_CTX: 'Recipe Search',
            LIST_HEADING_CTX: f"Results of <em>{search_term}</em>",
            READ_ONLY_CTX: False,
            LIST_SUB_HEADING_CTX: invalid_terms,
            REPEAT_SEARCH_TERM_CTX: query_search_term(
                query_params, exclude_queries=REORDER_REQ_QUERY_ARGS)
        }

    def add_no_content_context(self, context: dict) -> dict:
        """
        Add no content-specific info to context
        :param context: context
        :return: context
        """
        super().add_no_content_context(context)
        if self.has_no_content(context):
            self.render_no_content_help(
                context, "see_search_terms_help_msg.html")

        return context
