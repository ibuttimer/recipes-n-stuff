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
from typing import Dict, Optional

from base.dto import BaseDto
from checkout.models import Currency


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
    currencies = {
        currency.code: CurrencyDto.from_model(currency) for currency in list(
            Currency.objects.all()
        )
    }
    return currencies


def get_currencies():
    """
    Get the currencies dict
    :return: dict of currencies
    """
    global _CURRENCIES
    if _CURRENCIES is None:
        _CURRENCIES = build_currencies()
    return _CURRENCIES.copy()
