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

from .content_list_mixin import (
    TITLE_CTX, PAGE_HEADING_CTX, LIST_HEADING_CTX, LIST_SUB_HEADING_CTX,
    REPEAT_SEARCH_TERM_CTX, NO_CONTENT_MSG_CTX, NO_CONTENT_HELP_CTX,
    READ_ONLY_CTX, SUBMIT_URL_CTX, SUBMIT_BTN_TEXT_CTX, STATUS_CTX,
    SNIPPETS_CTX, ContentListMixin
)
from .enums import (
    ChoiceArg, QueryArg, SortOrder, PerPage, QueryOption, YesNo
)
from .file import find_parent_of_folder
from .forms import (
    update_field_widgets, error_messages, ErrorMsgs, form_auto_id, FormMixin
)
from .html import add_navbar_attr
from .misc import (
    Crud, permission_name, permission_check, ensure_list, find_index
)
from .models import (
    ModelMixin, ModelFacadeMixin,
    DESC_LOOKUP, DATE_OLDEST_LOOKUP, DATE_NEWEST_LOOKUP
)
from .query_params import QuerySetParams
from .queries import get_yes_no_ignore_query
from .search import (
    ORDER_QUERY, PAGE_QUERY, PER_PAGE_QUERY, REORDER_QUERY, SEARCH_QUERY,
    USER_QUERY, REORDER_REQ_QUERY_ARGS, DATE_QUERIES,
    regex_matchers, regex_date_matchers,
    KEY_TERM_GROUP, TERM_GROUP,
    DATE_KEY_TERM_GROUP, DATE_QUERY_GROUP, DATE_QUERY_DAY_GROUP,
    DATE_QUERY_MTH_GROUP, DATE_QUERY_YR_GROUP
)
from .url_path import (
    append_slash, namespaced_url, app_template_path, url_path, reverse_q,
    GET, PATCH, POST, DELETE
)
from .views import (
    redirect_on_success_or_render, resolve_req, redirect_payload,
    replace_html_payload, replace_inner_html_payload, rewrite_payload
)


__all__ = [
    'TITLE_CTX',
    'PAGE_HEADING_CTX',
    'LIST_HEADING_CTX',
    'LIST_SUB_HEADING_CTX',
    'REPEAT_SEARCH_TERM_CTX',
    'NO_CONTENT_MSG_CTX',
    'NO_CONTENT_HELP_CTX',
    'READ_ONLY_CTX',
    'SUBMIT_URL_CTX',
    'SUBMIT_BTN_TEXT_CTX',
    'STATUS_CTX',
    'SNIPPETS_CTX',
    'ContentListMixin',

    'ChoiceArg',
    'QueryArg',
    'SortOrder',
    'PerPage',
    'QueryOption',
    'YesNo',

    'find_parent_of_folder',

    'update_field_widgets',
    'error_messages',
    'ErrorMsgs',
    'form_auto_id',
    'FormMixin',

    'Crud',
    'permission_name',
    'permission_check',
    'ensure_list',
    'find_index',

    'add_navbar_attr',

    'ModelMixin',
    'ModelFacadeMixin',
    'DESC_LOOKUP',
    'DATE_OLDEST_LOOKUP',
    'DATE_NEWEST_LOOKUP',

    'QuerySetParams',

    'get_yes_no_ignore_query',

    'ORDER_QUERY',
    'PAGE_QUERY',
    'PER_PAGE_QUERY',
    'REORDER_QUERY',
    'SEARCH_QUERY',
    'USER_QUERY',
    'REORDER_REQ_QUERY_ARGS',
    'DATE_QUERIES',
    'regex_matchers',
    'regex_date_matchers',
    'KEY_TERM_GROUP',
    'TERM_GROUP',
    'DATE_KEY_TERM_GROUP',
    'DATE_QUERY_GROUP',
    'DATE_QUERY_DAY_GROUP',
    'DATE_QUERY_MTH_GROUP',
    'DATE_QUERY_YR_GROUP',

    'append_slash',
    'namespaced_url',
    'app_template_path',
    'url_path',
    'reverse_q',
    'GET',
    'PATCH',
    'POST',
    'DELETE',

    'redirect_on_success_or_render',
    'resolve_req',
    'redirect_payload',
    'replace_html_payload',
    'replace_inner_html_payload',
    'rewrite_payload',
]
