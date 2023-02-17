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

from django.db import models
from django.utils.translation import gettext_lazy as _

from utils import ModelMixin

from .constants import (
    CURRENCY_CODE_MAX_LEN, CURRENCY_CODE_FIELD, NUMERIC_CODE_FIELD,
    DIGITS_CODE_FIELD, NAME_FIELD, TIMESTAMP_FIELD, BASE_FIELD, RATES_FIELD,
    SYMBOL_FIELD
)


class Currency(ModelMixin, models.Model):
    """
    Currency information model
    """
    # field names
    CURRENCY_CODE_FIELD = CURRENCY_CODE_FIELD
    NUMERIC_CODE_FIELD = NUMERIC_CODE_FIELD
    DIGITS_CODE_FIELD = DIGITS_CODE_FIELD
    NAME_FIELD = NAME_FIELD
    SYMBOL_FIELD = SYMBOL_FIELD

    CURRENCY_ATTRIB_CODE_MAX_LEN: int = CURRENCY_CODE_MAX_LEN
    CURRENCY_ATTRIB_NAME_MAX_LEN: int = 100
    CURRENCY_ATTRIB_SYMBOL_MAX_LEN: int = 10

    code = models.CharField(
        _('currency code'), max_length=CURRENCY_ATTRIB_CODE_MAX_LEN,
        blank=False)

    numeric_code = models.IntegerField(
        _('numeric code'), blank=False, default=0)

    digits = models.IntegerField(
        _('number of digits'), blank=False, default=2)

    name = models.CharField(
        _('currency name'), max_length=CURRENCY_ATTRIB_NAME_MAX_LEN,
        blank=False)

    symbol = models.CharField(
        _('currency symbol'), max_length=CURRENCY_ATTRIB_SYMBOL_MAX_LEN,
        blank=False, default='¤')

    @dataclass
    class Meta:
        """ Model metadata """

    def __str__(self):
        return f'{self.code} {self.name}'


class CurrencyRate(ModelMixin, models.Model):
    """
    Currency rate data model
    """
    # field names
    TIMESTAMP_FIELD = TIMESTAMP_FIELD
    BASE_FIELD = BASE_FIELD
    RATES_FIELD = RATES_FIELD

    CURRENCY_RATE_ATTRIB_CODE_MAX_LEN: int = CURRENCY_CODE_MAX_LEN
    CURRENCY_RATE_ATTRIB_NAME_MAX_LEN: int = 3000

    timestamp = models.DateTimeField(_('timestamp'), blank=False)

    base = models.CharField(
        _('base currency'), max_length=CURRENCY_RATE_ATTRIB_CODE_MAX_LEN,
        blank=False)

    rates = models.BinaryField(
        _('rates'), blank=False, max_length=CURRENCY_RATE_ATTRIB_NAME_MAX_LEN)

    @dataclass
    class Meta:
        """ Model metadata """

    def __str__(self):
        return f'{self.timestamp} {self.base}'
