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
import json
from datetime import datetime, timezone
from enum import Enum, auto
from http import HTTPStatus
import zlib
from typing import Dict, Tuple, Union
from decimal import Decimal

import requests
from django.db.models import QuerySet
from requests import Response

from checkout.currency import get_currency
from checkout.models import CurrencyRate
from utils import GET

from recipesnstuff.settings import (
    EXCHANGERATES_DATA_KEY, DEFAULT_CURRENCY, DEFAULT_RATES_REQUEST_INTERVAL
)


def request_latest_rates() -> Response:
    """
    Get the latest rates from the rate API
    :return: response
    """
    url = f"https://api.apilayer.com/exchangerates_data/latest?" \
          f"base={DEFAULT_CURRENCY}"

    return requests.request(GET, url, headers={
        "apikey": EXCHANGERATES_DATA_KEY
    })


def get_rates() -> Tuple[Dict[str, float], str]:
    """
    Get the currency exchange rates
    :return: tuple of rates dict and base currency code
    """
    # check for rates within request interval
    order = CurrencyRate.date_lookup(
        CurrencyRate.TIMESTAMP_FIELD, oldest_first=False)

    query = CurrencyRate.objects.filter(**{
        f'{CurrencyRate.TIMESTAMP_FIELD}__gte':
            datetime.now(tz=timezone.utc) - DEFAULT_RATES_REQUEST_INTERVAL
    }).order_by(order)

    def rates_from_query(rquery: QuerySet) -> Tuple[Dict[str, float], str]:
        db_entry = rquery.all()[0]
        db_rates = json.loads(
            zlib.decompress(db_entry.rates)
        )
        return db_rates, db_entry.base

    if query.count() > 0:
        # use rates from database
        rates, base = rates_from_query(query)
    else:
        # request rates
        response = request_latest_rates()
        if response.status_code == HTTPStatus.OK:
            rjson = response.json()
            rates = rjson['rates']
            base = rjson['base']

            CurrencyRate.objects.create(**{
                f'{CurrencyRate.TIMESTAMP_FIELD}': datetime.now(tz=timezone.utc),
                f'{CurrencyRate.BASE_FIELD}': base,
                f'{CurrencyRate.RATES_FIELD}': zlib.compress(
                    bytes(json.dumps(rates),'UTF-8')
                )
            })
        else:
            # use latest from database
            rates, base = rates_from_query(
                CurrencyRate.objects.order_by(order))

    return rates, base


class NumType(Enum):
    """ Enum representing numeric types"""
    INT = auto()
    FLOAT = auto()
    DECIMAL = auto()


def convert_forex(
        amount: Union[int, float, Decimal], from_ccy: str, to_ccy: str,
        count: int = 1, smallest_unit: bool = False, factor: int = -1,
        result_as: NumType = NumType.FLOAT) -> Union[int, float, Decimal]:
    """
    Convert `amount` from `from_ccy` to `to_ccy`
    :param amount: amount to convert
    :param from_ccy: code of currency to convert from
    :param to_ccy: code of currency to convert to
    :param count: unit count: default 1
    :param smallest_unit: smallest currency unit flag; default False
    :param factor: number of digits to normalise result to;
            default currency digits, ignored when smallest_unit is True and
            set to None for max possible precision
    :param result_as: result type; default float,
            ignored when smallest_unit is True
    :return: converted amount
    """
    rates, _ = get_rates()
    from_ccy = from_ccy.upper()
    to_ccy = to_ccy.upper()
    if from_ccy not in rates or to_ccy not in rates:
        raise ValueError(f'Unknown currency codes; {from_ccy} or {to_ccy}')

    value = amount if isinstance(amount, Decimal) \
        else Decimal.from_float(amount)
    value *= count

    if from_ccy != to_ccy:
        rate = Decimal.from_float(rates[to_ccy]) / \
               Decimal.from_float(rates[from_ccy])
        value *= rate

    return normalise_amount(
        value, to_ccy, smallest_unit=smallest_unit, factor=factor,
        result_as=result_as)


def normalise_amount(
        amount: Union[int, float, Decimal], ccy: str,
        smallest_unit: bool = False, factor: int = -1,
        result_as: NumType = NumType.FLOAT) -> Union[int, float, Decimal]:
    """
    Convert `amount` from `from_ccy` to `to_ccy`
    :param amount: amount to convert
    :param ccy: code of currency
    :param smallest_unit: smallest currency unit flag; default False
    :param factor: number of digits to normalise result to;
            default currency digits, ignored when smallest_unit is True and
            set to None for max possible precision
    :param result_as: result type; default float,
            ignored when smallest_unit is True
    :return: normalised amount
    """
    value = amount if isinstance(amount, Decimal) \
        else Decimal.from_float(amount)

    currency = get_currency(ccy)

    if smallest_unit:
        # smallest unit is always an int
        factor = Decimal(10) ** currency.digits
        value = int(value * factor)
        if currency.digits == 3:
            # must round amounts to the nearest ten
            value = round(value/10, 1) * 10
    else:
        if factor is not None:
            factor = Decimal(10) ** (
                -currency.digits if factor < 0 else -factor
            )
            value = value.quantize(factor)
        if result_as == NumType.FLOAT:
            value = float(value)
        elif result_as == NumType.INT:
            value = int(value)

    return value
