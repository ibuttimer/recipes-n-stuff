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
from collections import namedtuple
from dataclasses import dataclass
from enum import Enum
from typing import TypeVar, List, Tuple
from decimal import Decimal
from datetime import timedelta, datetime, MINYEAR, timezone

from django.db import models
from django.utils.translation import gettext_lazy as _

import ccy

from recipesnstuff.settings import DEFAULT_CURRENCY
from user.models import User
from utils import ModelMixin

from .constants import (
    NAME_FIELD, FREQUENCY_FIELD, FREQUENCY_TYPE_FIELD, AMOUNT_FIELD,
    DESCRIPTION_FIELD, IS_ACTIVE_FIELD, USER_FIELD, SUBSCRIPTION_FIELD,
    START_DATE_FIELD, END_DATE_FIELD, BASE_CURRENCY_FIELD
)

# workaround for self type hints from https://peps.python.org/pep-0673/
TypeMeasure = TypeVar("TypeMeasure", bound="Measure")


Frequency = namedtuple('Frequency', ['name', 'choice'])


class FrequencyType(Enum):
    """ Enum representing subscription frequency types """
    WEEKLY = Frequency('Weekly', 'mt')
    MONTHLY = Frequency('Monthly', 'mt')
    YEARLY = Frequency('Yearly', 'yr')


def get_frequency_choices() -> List[Tuple]:
    """
    Get the frequency type choices
    :return: list of choices
    """
    return [
        (sub.value.choice, sub.value.name) for sub in FrequencyType
    ]


class Subscription(ModelMixin, models.Model):
    """
    Subscription model
    """
    # field names
    NAME_FIELD = NAME_FIELD
    FREQUENCY_TYPE_FIELD = FREQUENCY_TYPE_FIELD
    FREQUENCY_FIELD = FREQUENCY_FIELD
    AMOUNT_FIELD = AMOUNT_FIELD
    BASE_CURRENCY_FIELD = BASE_CURRENCY_FIELD
    DESCRIPTION_FIELD = DESCRIPTION_FIELD
    IS_ACTIVE_FIELD = IS_ACTIVE_FIELD

    SUBSCRIPTION_ATTRIB_NAME_MAX_LEN: int = 50
    SUBSCRIPTION_ATTRIB_DESCRIPTION_MAX_LEN: int = 250
    SUBSCRIPTION_ATTRIB_CURRENCY_CODE_MAX_LEN: int = 3

    SUBSCRIPTION_FREQUENCY_DEFAULT: int = 1

    name = models.CharField(
        _('name'), max_length=SUBSCRIPTION_ATTRIB_NAME_MAX_LEN,
        blank=False, unique=True)

    frequency_type = models.CharField(
        _('frequency type'), max_length=2,
        choices=get_frequency_choices(),
        default=FrequencyType.MONTHLY.value.choice,
    )

    frequency = models.IntegerField(
        _('frequency'), default=SUBSCRIPTION_FREQUENCY_DEFAULT)

    amount = models.DecimalField(
        _('amount'), default=Decimal.from_float(0), decimal_places=6,
        max_digits=19)

    base_currency = models.CharField(
        _('base currency'),
        max_length=SUBSCRIPTION_ATTRIB_CURRENCY_CODE_MAX_LEN, blank=False,
        default=ccy.currency(DEFAULT_CURRENCY).code)

    description = models.CharField(
        _('name'), max_length=SUBSCRIPTION_ATTRIB_NAME_MAX_LEN, blank=False)

    is_active = models.BooleanField(
        _('is active'), default=False, blank=False, help_text=_(
            "Designates that this record is active."
        ))

    @dataclass
    class Meta:
        """ Model metadata """

    def __str__(self):
        return f'{self.name}'


class UserSubscription(ModelMixin, models.Model):
    """
    User subscription model
    """
    # field names
    USER_FIELD = USER_FIELD
    SUBSCRIPTION_FIELD = SUBSCRIPTION_FIELD
    START_DATE_FIELD = START_DATE_FIELD
    END_DATE_FIELD = END_DATE_FIELD
    IS_ACTIVE_FIELD = IS_ACTIVE_FIELD

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE)

    start_date = models.DateTimeField(_('start date'), auto_now_add=True)

    end_date = models.DateTimeField(
        _('End date'), default=datetime(MINYEAR, 1, 1, tzinfo=timezone.utc))

    is_active = models.BooleanField(
        _('is active'), default=False, blank=False, help_text=_(
            "Designates that this record is active."
        ))

    @dataclass
    class Meta:
        """ Model metadata """

    def __str__(self):
        return f'{self.user} {self.subscription} {self.start_date} ' \
               f'{self.end_date} {self.is_active}'
