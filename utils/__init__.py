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

from .file import find_parent_of_folder
from .forms import update_field_widgets, error_messages, ErrorMsgs
from .html import add_navbar_attr
from .models import (
    ModelMixin, ModelFacadeMixin,
    DESC_LOOKUP, DATE_OLDEST_LOOKUP, DATE_NEWEST_LOOKUP
)
from .url_path import (
    append_slash, namespaced_url, app_template_path, url_path, reverse_q
)
from .views import redirect_on_success_or_render, resolve_req


__all__ = [
    'find_parent_of_folder',

    'update_field_widgets',
    'error_messages',
    'ErrorMsgs',

    'add_navbar_attr',

    'ModelMixin',
    'ModelFacadeMixin',
    'DESC_LOOKUP',
    'DATE_OLDEST_LOOKUP',
    'DATE_NEWEST_LOOKUP',

    'append_slash',
    'namespaced_url',
    'app_template_path',
    'url_path',
    'reverse_q',

    'redirect_on_success_or_render',
    'resolve_req',
]
