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
    has_permission: bool
    active: bool
    disabled: bool


def add_navbar_attr(context: dict, key: str, is_active: bool = False,
                    has_permission: bool = True, disabled: bool = False,
                    a_xtra: str = None, span_xtra: str = None,
                    is_dropdown_toggle: bool = False) -> dict:
    """
    Add navbar attributes from the specified key
    :param context: context for template
    :param key: context key
    :param is_active: is active flag; default False
    :param has_permission: has_permission flag; default True
    :param disabled: is disabled flag; default False
    :param a_xtra: extra classes for 'a' tag; default None
    :param span_xtra: extra classes for 'span' tag; default None
    :param is_dropdown_toggle: dropdown toggle flag; default False
    :return: context
    """
    dropdown_toggle = 'dropdown-toggle' if is_dropdown_toggle else ''
    if is_active:
        a_attr = f'class="nav-link {dropdown_toggle} {a_xtra or ""} active active_page" ' \
                 f'aria-current="page"'
        span_attr = f'class="{span_xtra or ""}"'
    else:
        a_attr = f'class="nav-link {dropdown_toggle} {a_xtra or ""}"'
        span_attr = f'class="{span_xtra or ""}"'

    context[key] = NavbarAttr(
        a_attr=a_attr, span_attr=span_attr, has_permission=has_permission,
        active=is_active, disabled=disabled)

    return context
