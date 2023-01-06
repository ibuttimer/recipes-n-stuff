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
import re
from re import Pattern
from typing import Any

from .enums import QueryOption

# chars used to delimit queries
MARKER_CHARS = ['=', '"', "'"]

# common request query keys
ORDER_QUERY: str = 'order'              # opinion order
PAGE_QUERY: str = 'page'                # page number
PER_PAGE_QUERY: str = 'per-page'        # pagination per page
REORDER_QUERY: str = 'reorder'          # reordering of previous query
SEARCH_QUERY: str = 'search'            # search from search box in header
USER_QUERY: str = 'user'                # username

# args for an ajax reorder/next page/etc. request
REORDER_REQ_QUERY_ARGS = [
    ORDER_QUERY, PAGE_QUERY, PER_PAGE_QUERY, REORDER_QUERY
]

# Note: a search can have any of the following queries embedded in its
# value
ON_OR_AFTER_QUERY: str = 'on-or-after'      # search >= date
ON_OR_BEFORE_QUERY: str = 'on-or-before'    # search <= date
AFTER_QUERY: str = 'after'                  # search > date
BEFORE_QUERY: str = 'before'                # search < date
EQUAL_QUERY: str = 'date'                   # search == date

DATE_QUERIES = [
    ON_OR_AFTER_QUERY, ON_OR_BEFORE_QUERY, AFTER_QUERY, BEFORE_QUERY,
    EQUAL_QUERY
]
# date query request arguments for a search request
DATE_QUERY_ARGS = [
    QueryOption.of_no_cls_dflt(query) for query in DATE_QUERIES
]


KEY_TERM_GROUP = 1  # match group of required text & key of non-date terms
TERM_GROUP = 3      # match group of required text of non-date terms


def regex_pattern(mark: str, pattern: str) -> Pattern[Any]:
    """
    Compile a regex pattern for query params
    :param mark: query key
    :param pattern: value pattern
    :return: compiled regex
    """
    return re.compile(
        # match single/double-quoted text after 'mark='
        # if 'mark=' is not preceded by a non-space
        rf'.*(?<!\S)({mark}=(?P<quote>[\'\"])({pattern})(?P=quote))\s*.*',
        re.IGNORECASE)


def regex_matchers(queries: list[str]) -> dict:
    """
    Generate regex matchers for specified query terms
    :param queries: list of query terms to generate matchers for
    :return: matchers
    """
    return {
        q: regex_pattern(mark, r'.*?') for q, mark in [
            # use query term as marker
            (qm, qm) for qm in queries
        ]
    }


DATE_SEP = '-'
SLASH_SEP = '/'
DOT_SEP = '.'
SPACE_SEP = ' '
DATE_SEPARATORS = [
    DATE_SEP, SLASH_SEP, DOT_SEP, SPACE_SEP
]
SEP_REGEX = rf'[{"".join(DATE_SEPARATORS)}]'
DMY_REGEX = r'(\d+)(?P<sep>[-/. ])(\d+)(?P=sep)(\d*)'


DATE_KEY_TERM_GROUP = 1     # match group of required text & key of date terms
DATE_QUERY_GROUP = 2        # match group of required text
DATE_QUERY_DAY_GROUP = 4    # match group of day text
DATE_QUERY_MTH_GROUP = 6    # match group of month text
DATE_QUERY_YR_GROUP = 7     # match group of year text


def regex_date_matchers() -> dict:
    """
    Generate regex matchers for date query terms
    :return: matchers
    """
    return {
        # match single/double-quoted date after 'xxx='
        # if 'xxx=' is not preceded by a non-space
        q: regex_pattern(mark, DMY_REGEX) for q, mark in [
            # use query term as marker
            (qm, qm) for qm in DATE_QUERIES
        ]
    }
