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
from copy import deepcopy
from dataclasses import dataclass
from typing import Dict, Optional

from django.db import connection

from base.dto import BaseDto

from .constants import (
    ZERO_DECIMAL_CURRENCIES, THREE_DECIMAL_CURRENCIES, THIS_APP
)
from .models import Currency


@dataclass
class CurrencyDto(BaseDto):

    @staticmethod
    def from_model(currency: Currency):
        """
        Generate a DTO from the specified `model`
        :param currency: model instance to populate DTO from
        :return: DTO instance
        """
        dto = BaseDto.from_model_to_obj(currency, Currency())
        # custom handling for specific attributes
        return dto


_CURRENCIES: Optional[Dict[str, CurrencyDto]] = None


def build_currencies() -> Dict[str, CurrencyDto]:
    """
    Build the currencies
    :return: dict of currencies
    """
    # in some tests, currency table may not have been created yet
    all_tables = connection.introspection.table_names()
    currency_list = [] if f'{THIS_APP}_{Currency.model_name()}'.lower() \
                          not in all_tables else list(Currency.objects.all())

    currencies = {
        currency.code: CurrencyDto.from_model(currency)
        for currency in currency_list
    }

    for code in ZERO_DECIMAL_CURRENCIES:
        if code in currencies:
            assert currencies[code].digits == 0

    for code in THREE_DECIMAL_CURRENCIES:
        if code in currencies:
            assert currencies[code].digits == 3

    return currencies


def get_currencies(copy: bool = True):
    """
    Get the currencies dict
    :param copy: return a copy flag; default True
    :return: dict of currencies
    """
    global _CURRENCIES
    if _CURRENCIES is None or len(_CURRENCIES) == 0:
        _CURRENCIES = build_currencies()
    return deepcopy(_CURRENCIES) if copy else _CURRENCIES


def get_currency(code: str) -> CurrencyDto:
    """
    Get a currency
    :param code: currency code
    :return: currency dto
    """
    currencies = get_currencies(copy=False)
    return deepcopy(currencies[code])
