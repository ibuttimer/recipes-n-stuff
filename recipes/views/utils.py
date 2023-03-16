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
import re
from datetime import timedelta
from typing import Union, List, Tuple

from django.http import HttpRequest

from timedelta_isoformat import timedelta as timedelta_iso

from recipes.constants import THIS_APP
from recipes.models import Recipe, Category
from utils import (
    Crud, permission_check
)


YEAR = 'y'
MTH = 'mth'
WK = 'w'
DAY = 'd'
HOUR = 'h'
MIN = 'min'
SEC = 's'
# word boundary/digits/(optional spaces)/symbol/word boundary
DURATION_REGEX = re.compile(
    rf'(\b(\d+)\s*({YEAR}|{MTH}|{WK}|{DAY}|{HOUR}|{MIN}|{SEC})\b)',
    flags=re.IGNORECASE)

ALL_DURATION_SYMBOLS = [YEAR, MTH, WK, DAY, HOUR, MIN, SEC]
DURATION_FORMAT_STR = ' '.join(list(map(
    lambda s: f'#{s}', ALL_DURATION_SYMBOLS
)))

DAYS_PER_MTH = 31
DAYS_PER_YEAR = 365
MTHS_PER_YEAR = 12

ISO_PERIOD = 'P'
ISO_YEAR = 'Y'
ISO_MTH = 'M'
ISO_DAY = 'D'
ISO_TIME = 'T'
ISO_HOUR = 'H'
ISO_MIN = 'M'
ISO_SEC = 'S'


def recipe_permission_check(
        request: HttpRequest,
        perm_op: Union[Union[Crud, str], List[Union[Crud, str]]],
        raise_ex: bool = True) -> bool:
    """
    Check request user has specified permission
    :param request: http request
    :param perm_op: Crud operation or permission name to check
    :param raise_ex: raise exception; default True
    """
    return permission_check(request, Recipe, perm_op,
                            app_label=THIS_APP, raise_ex=raise_ex)


def category_permission_check(
        request: HttpRequest,
        perm_op: Union[Union[Crud, str], List[Union[Crud, str]]],
        raise_ex: bool = True) -> bool:
    """
    Check request user has specified permission
    :param request: http request
    :param perm_op: Crud operation or permission name to check
    :param raise_ex: raise exception; default True
    """
    return permission_check(request, Category, perm_op,
                            app_label=THIS_APP, raise_ex=raise_ex)


def parse_duration(duration: str) -> Tuple[bool, timedelta]:
    """
    Parse a duration string
    :param duration: string to parse
    :return: tuple of 'is valid' flag and timedelta
    """
    decoded = {}
    error = False
    term_set = set()

    is_valid = isinstance(duration, timedelta)
    if is_valid:
        delta = duration
    else:
        match = True
        search_str = duration.strip()
        start_pos = 0
        while match:
            match = DURATION_REGEX.search(search_str, pos=start_pos)
            if match:
                pre_str = search_str[start_pos:match.start(2)]
                if len(pre_str) > 0:
                    ws_match = re.match(r'\s+', pre_str)
                    if not ws_match or ws_match.end(0) != len(pre_str):
                        # only whitespace allowed before number
                        error = True
                        break

                # groups should match in 3's; whole, number and symbol match
                # e.g ('1s', '1', 's')
                whole = match.group(1).replace(' ', '')
                digits = match.group(2)
                symbol = match.group(3).lower()
                if whole.isalnum() and digits.isnumeric() and symbol.isalpha():
                    factor = 1
                    if symbol == SEC:
                        key = 'seconds'
                    elif symbol == MIN:
                        key = 'minutes'
                    elif symbol == HOUR:
                        key = 'hours'
                    elif symbol == DAY:
                        key = 'days'
                    elif symbol == WK:
                        key = 'weeks'
                    elif symbol == MTH:
                        key = 'days'
                        factor = DAYS_PER_MTH
                    elif symbol == YEAR:
                        key = 'days'
                        factor = DAYS_PER_YEAR
                    else:
                        raise ValueError(f'Unknown symbol {symbol}')

                    if symbol in term_set:
                        # duplicate symbols are not allowed
                        error = True
                        break

                    term_set.add(symbol)
                    value = int(digits) * factor
                    decoded[key] = decoded[key] + value \
                        if key in decoded else value
                    start_pos = match.end(3)
                else:
                    # invalid match
                    error = True
                    break

        is_valid = len(decoded) > 0 and not error
        delta = timedelta(**decoded) if is_valid else None

    return is_valid, delta


def encode_timedelta(delta: timedelta) -> str:
    """
    Encode a timedelta in input format
    :param delta: timedelta to encode
    :return: encoded info
    """
    td = timedelta_iso(days=delta.days, seconds=delta.seconds)
    # ISO_8601 durations: PnYnMnDTnHnMnS
    duration = td.isoformat()

    def cut(pstr, start, term):
        end = pstr.index(term) if term in pstr else start
        return pstr[start:end], end

    def normalise(units, tens, units_per_ten) -> Tuple:
        if units and int(units) >= units_per_ten:
            iunits = int(units)
            itens = int(iunits / units_per_ten)
            iunits -= (itens * units_per_ten)
            tens = str(itens + (int(tens) if tens else 0))
            units = str(iunits) if iunits else ''
        return units, tens

    # iso T will never be 0 as valid string starts with P
    tidx = duration.index(ISO_TIME) if ISO_TIME in duration else 0
    ymd = duration[1:tidx or len(duration)]
    time = duration[tidx + 1:] if tidx else ''
    year, mth, day, hour, minute, sec = (0, 0, 0, 0, 0, 0)

    if time:
        hour, end = cut(time, 0, ISO_HOUR)
        minute, end = cut(time, end + 1 if hour else end, ISO_MIN)
        sec, end = cut(time, end + 1 if minute else end, ISO_SEC)

        sec, minute = normalise(sec, minute, 60)
        minute, hour = normalise(minute, hour, 60)

    if ymd:
        year, end = cut(ymd, 0, ISO_YEAR)
        mth, end = cut(ymd, end + 1 if year else end, ISO_MTH)
        day, end = cut(ymd, end + 1 if mth else end, ISO_DAY)

        hour, day = normalise(hour, day, 24)
        day, mth = normalise(day, mth, DAYS_PER_MTH)
        mth, year = normalise(mth, year, MTHS_PER_YEAR)

    return ' '.join([
        f'{num}{symbol}' for num, symbol in [
            (year, YEAR), (mth, MTH), (day, DAY),
            (hour, HOUR), (minute, MIN), (sec, SEC)
        ] if num
    ])
