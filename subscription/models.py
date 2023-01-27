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
from typing import TypeVar, List, Tuple, Optional
from decimal import Decimal
from datetime import datetime, MINYEAR, timezone, timedelta

from django.db import models
from django.utils.translation import gettext_lazy as _

import ccy
from dateutil.relativedelta import *

from recipesnstuff.settings import DEFAULT_CURRENCY
from user.models import User
from utils import ModelMixin

from .constants import (
    NAME_FIELD, FREQUENCY_FIELD, FREQUENCY_TYPE_FIELD, AMOUNT_FIELD,
    DESCRIPTION_FIELD, IS_ACTIVE_FIELD, USER_FIELD, SUBSCRIPTION_FIELD,
    START_DATE_FIELD, END_DATE_FIELD, BASE_CURRENCY_FIELD, FEATURE_TYPE_FIELD,
    CALL_TO_PICK_FIELD, FEATURES_FIELD, COUNT_FIELD
)

# workaround for self type hints from https://peps.python.org/pep-0673/
TypeMeasure = TypeVar("TypeMeasure", bound="Measure")
TypeFrequencyType = TypeVar("FrequencyType", bound="FrequencyType")
TypeFeatureType = TypeVar("FeatureType", bound="FeatureType")


Frequency = namedtuple(
    'Frequency', [                                  # relativedelta keyword
        'name', 'choice', 'period', 'period_abbrev', 'rel_delta'
    ])
Feature = namedtuple('Feature', ['name', 'choice'])


class FrequencyType(Enum):
    """ Enum representing subscription frequency types """
    BY_MIN = Frequency('By the minute', 'mn', 'minute', 'min', 'minutes')
    HOURLY = Frequency('Hourly', 'hr', 'hour', 'hr', 'hours')
    DAILY = Frequency('Daily', 'dy', 'day', 'dy', 'days')
    WEEKLY = Frequency('Weekly', 'wk', 'week', 'wk', 'weeks')
    MONTHLY = Frequency('Monthly', 'mt', 'month', 'mth', 'months')
    YEARLY = Frequency('Yearly', 'yr', 'year', 'yr', 'years')

    def is_from_choice(self, choice: str) -> bool:
        """
        Check if the specified `choice` relates to this object
        :param choice: choice to check
        :return: True if choice matches
        """
        return self.value.choice == choice

    def timedelta(self, count: int) -> timedelta:
        """
        Generate the timedelta of this object with the specified count
        :param count: frequency to ge
        :return: timedelta
        """
        return relativedelta(**{
            f'{self.value.rel_delta}': count
        })

    @staticmethod
    def from_choice(choice: str) -> Optional[TypeFrequencyType]:
        """
        Get the FrequencyType corresponding to `choice`
        :param choice: choice to find
        :return: frequency type or None of not found
        """
        result = list(
            filter(lambda t: t.value.choice == choice, FrequencyType)
        )
        return result[0] if len(result) == 1 else None

    @property
    def namely(self):
        """ Namely value for this object """
        return self.value.name

    @property
    def choice(self):
        """ Choice value for this object """
        return self.value.choice

    @property
    def period(self):
        """ Period value for this object """
        return self.value.period

    @property
    def period_abbrev(self):
        """ Abbreviated period value for this object """
        return self.value.period_abbrev


def get_frequency_choices() -> List[Tuple]:
    """
    Get the frequency type choices
    :return: list of choices
    """
    return [
        (sub.value.choice, sub.value.name) for sub in FrequencyType
    ]


class FeatureType(Enum):
    """ Enum representing subscription feature types """
    BASIC = Feature('Basic', 'ba')
    FREE_DELIVERY = Feature('Free delivery', 'fd')
    FREE_DELIVERY_OVER = Feature('Free delivery over', 'fdo')
    FREE_DELIVERY_AFTER = Feature('Free delivery after', 'fda')
    FREE_CLASSES = Feature('Free classes', 'fc')
    FIRST_X_FREE = Feature('First number of items free', 'xif')
    FREE_AFTER_SPEND = Feature('Free after spending', 'fas')

    @staticmethod
    def from_choice(choice: str) -> Optional[TypeFeatureType]:
        """
        Get the FeatureType corresponding to `choice`
        :param choice: choice to find
        :return: feature type or None of not found
        """
        result = list(
            filter(lambda t: t.value.choice == choice, FeatureType)
        )
        return result[0] if len(result) == 1 else None

    @property
    def feature_name(self):
        """ Name value for this object """
        return self.value.choice

    @property
    def choice(self):
        """ Choice value for this object """
        return self.value.choice


def get_feature_choices() -> List[Tuple]:
    """
    Get the feature type choices
    :return: list of choices
    """
    return [
        (sub.value.choice, sub.value.name) for sub in FeatureType
    ]


class SubscriptionFeature(ModelMixin, models.Model):
    """
    Subscription features model
    """
    # field names
    DESCRIPTION_FIELD = DESCRIPTION_FIELD
    FEATURE_TYPE_FIELD = FEATURE_TYPE_FIELD
    AMOUNT_FIELD = AMOUNT_FIELD
    COUNT_FIELD = COUNT_FIELD
    BASE_CURRENCY_FIELD = BASE_CURRENCY_FIELD
    IS_ACTIVE_FIELD = IS_ACTIVE_FIELD

    FEATURE_ATTRIB_FEAT_TYPE_MAX_LEN: int = 3
    FEATURE_ATTRIB_DESCRIPTION_MAX_LEN: int = 250
    FEATURE_ATTRIB_CURRENCY_CODE_MAX_LEN: int = 3

    FEATURE_AMOUNT_TEMPLATE_MARK = f'{{{AMOUNT_FIELD}}}'
    FEATURE_COUNT_TEMPLATE_MARK = f'{{{COUNT_FIELD}}}'

    description = models.CharField(
        _('description'), max_length=FEATURE_ATTRIB_DESCRIPTION_MAX_LEN,
        blank=False)

    feature_type = models.CharField(
        _('feature type'), max_length=FEATURE_ATTRIB_FEAT_TYPE_MAX_LEN,
        choices=get_feature_choices(),
        default=FeatureType.BASIC.value.choice,
    )

    amount = models.DecimalField(
        _('amount'), default=Decimal.from_float(0), decimal_places=2,
        max_digits=19)

    base_currency = models.CharField(
        _('base currency'),
        max_length=FEATURE_ATTRIB_CURRENCY_CODE_MAX_LEN, blank=False,
        default=ccy.currency(DEFAULT_CURRENCY).code)

    count = models.IntegerField(_('count'), default=0)

    is_active = models.BooleanField(
        _('is active'), default=False, blank=False, help_text=_(
            "Designates that this record is active."
        ))

    @dataclass
    class Meta:
        """ Model metadata """

    @classmethod
    def numeric_fields(cls) -> list[str]:
        """ Get the list of numeric fields """
        return [SubscriptionFeature.AMOUNT_FIELD]

    def __str__(self):
        return f'{self.feature_type} {self.description} {self.amount} ' \
               f'{self.base_currency}/{self.count}'


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
    CALL_TO_PICK_FIELD = CALL_TO_PICK_FIELD
    FEATURES_FIELD = FEATURES_FIELD
    IS_ACTIVE_FIELD = IS_ACTIVE_FIELD

    SUBSCRIPTION_ATTRIB_FREQ_TYPE_MAX_LEN: int = 2
    SUBSCRIPTION_ATTRIB_NAME_MAX_LEN: int = 50
    SUBSCRIPTION_ATTRIB_DESCRIPTION_MAX_LEN: int = 250
    SUBSCRIPTION_ATTRIB_CURRENCY_CODE_MAX_LEN: int = \
        SubscriptionFeature.FEATURE_ATTRIB_CURRENCY_CODE_MAX_LEN
    SUBSCRIPTION_ATTRIB_CALL_TO_PICK_MAX_LEN: int = 50

    SUBSCRIPTION_FREQUENCY_DEFAULT: int = 1

    name = models.CharField(
        _('name'), max_length=SUBSCRIPTION_ATTRIB_NAME_MAX_LEN,
        blank=False, unique=True)

    frequency_type = models.CharField(
        _('frequency type'), max_length=SUBSCRIPTION_ATTRIB_FREQ_TYPE_MAX_LEN,
        choices=get_frequency_choices(),
        default=FrequencyType.MONTHLY.value.choice,
    )

    frequency = models.IntegerField(
        _('frequency'), default=SUBSCRIPTION_FREQUENCY_DEFAULT)

    amount = models.DecimalField(
        _('amount'), default=Decimal.from_float(0), decimal_places=2,
        max_digits=19)

    base_currency = models.CharField(
        _('base currency'),
        max_length=SUBSCRIPTION_ATTRIB_CURRENCY_CODE_MAX_LEN, blank=False,
        default=ccy.currency(DEFAULT_CURRENCY).code)

    description = models.CharField(
        _('description'), max_length=SUBSCRIPTION_ATTRIB_DESCRIPTION_MAX_LEN,
        blank=False)

    call_to_pick = models.CharField(
        _('reason to pick'),
        max_length=SUBSCRIPTION_ATTRIB_CALL_TO_PICK_MAX_LEN,
        blank=False, default='Select')

    features = models.ManyToManyField(SubscriptionFeature)

    is_active = models.BooleanField(
        _('is active'), default=False, blank=False, help_text=_(
            "Designates that this record is active."
        ))

    @dataclass
    class Meta:
        """ Model metadata """

    @classmethod
    def numeric_fields(cls) -> list[str]:
        """ Get the list of numeric fields """
        return [Subscription.FREQUENCY_FIELD, Subscription.AMOUNT_FIELD]

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

    @classmethod
    def date_fields(cls) -> list[str]:
        """ Get the list of date fields """
        return [
            UserSubscription.START_DATE_FIELD, UserSubscription.END_DATE_FIELD
        ]

    def __str__(self):
        return f'{self.user} {self.subscription} {self.start_date} ' \
               f'{self.end_date} {self.is_active}'
