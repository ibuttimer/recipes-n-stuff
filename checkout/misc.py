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
from typing import Union
from decimal import Decimal

from checkout.currency import get_currency
from checkout.forex import NumType, convert_forex
from recipesnstuff.settings import FINANCIAL_FACTOR


def massage_amount(amount: Union[int, Decimal, float],
                   as_decimal: bool = False) -> Union[int, float, Decimal]:
    """
    Massage amount into the desired format
    :param amount: item amount
    :param as_decimal: as Decimal flag; default False
    :return: amount
    """
    return amount if not as_decimal else amount \
        if isinstance(amount, Decimal) else Decimal.from_float(amount)


def calc_cost(amount: Union[Decimal, float], count: int,
              as_decimal: bool = False) -> Union[int, float, Decimal]:
    """
    Total cost in item base currency
    :param amount: item amount
    :param count: number of items
    :param as_decimal: as Decimal flag; default False
    :return: total cost
    """
    total = amount * count if not isinstance(amount, Decimal) else \
        amount * Decimal.from_float(count)
    return massage_amount(total, as_decimal=as_decimal)


def calc_ccy_cost(amount: Union[Decimal, float], from_ccy: str, to_ccy: str,
                  count: int = 1,
                  as_decimal: bool = False) -> Union[int, float, Decimal]:
    """
    Total cost in item base currency
    :param amount: item amount
    :param from_ccy: code of currency to convert from
    :param to_ccy: code of currency to convert to
    :param count: number of items; default 1
    :param as_decimal: as Decimal flag; default False
    :return: total cost
    """
    ccy_cnv = from_ccy != to_ccy
    total = calc_cost(amount, count, as_decimal=ccy_cnv)
    if ccy_cnv:
        total = convert_forex(total, from_ccy, to_ccy, factor=FINANCIAL_FACTOR,
                              result_as=NumType.DECIMAL)
    return massage_amount(total, as_decimal=as_decimal)


def format_amount_str(amt: float, code: str, with_symbol: bool = False):
    """
    Get a formatted amount string
    :param amt: amount
    :param code: currency code
    :param with_symbol: include currency symbol flag; default False
    :return: formatted string
    """
    currency = get_currency(code)
    symbol = f'{currency.symbol} ' if with_symbol else ''
    return f'{symbol}{amt:.{currency.digits}f}'
