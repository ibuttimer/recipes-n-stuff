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
from dataclasses import dataclass


@dataclass
class NavbarAttr:
    """ Navbar link attributes """
    a_attr: str
    span_attr: str


def add_navbar_attr(context: dict, key: str, is_active: bool = False,
                    a_xtra: str = None, span_xtra: str = None) -> dict:
    """
    Add navbar attributes from the specified key
    :param context: context for template
    :param key: context key
    :param is_active: is active flag; default False
    :param a_xtra: extra classes for 'a' tag; default None
    :param span_xtra: extra classes for 'span' tag; default None
    :return: context
    """
    context[key] = NavbarAttr(
        f'class="nav-link {a_xtra or ""} active" aria-current="page"',
        f'class="active_page {span_xtra or ""}"'
    ) if is_active else NavbarAttr(
        f'class="nav-link {a_xtra or ""}"',
        f'class="{span_xtra or ""}"'
    )
    return context