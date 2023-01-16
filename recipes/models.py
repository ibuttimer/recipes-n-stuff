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
from typing import TypeVar
from decimal import Decimal

from django.db import models
from django.db.models import DurationField
from django.utils.translation import gettext_lazy as _

from utils import ModelMixin

from .constants import (
    NAME_FIELD, TYPE_FIELD, SYSTEM_FIELD, IS_DEFAULT_FIELD, ABBREV_FIELD,
    BASE_US_FIELD, BASE_METRIC_FIELD, MEASURE_FIELD
)

# workaround for self type hints from https://peps.python.org/pep-0673/
TypeMeasure = TypeVar("TypeMeasure", bound="Measure")


class Category(ModelMixin, models.Model):
    """
    Category model
    """
    # field names
    NAME_FIELD = NAME_FIELD

    CATEGORY_ATTRIB_NAME_MAX_LEN: int = 50

    name = models.CharField(
        _('name'), max_length=CATEGORY_ATTRIB_NAME_MAX_LEN,
        blank=False, unique=True)

    @dataclass
    class Meta:
        """ Model metadata """

    def __str__(self):
        return f'{self.name}'


class Keyword(ModelMixin, models.Model):
    """
    Keyword model
    """
    # field names
    NAME_FIELD = NAME_FIELD

    KEYWORD_ATTRIB_NAME_MAX_LEN: int = 50

    name = models.CharField(
        _('name'), max_length=KEYWORD_ATTRIB_NAME_MAX_LEN,
        blank=False, unique=True)

    @dataclass
    class Meta:
        """ Model metadata """

    def __str__(self):
        return f'{self.name}'


class Measure(ModelMixin, models.Model):
    """
    Measure model
    """
    # field names
    TYPE_FIELD = TYPE_FIELD
    SYSTEM_FIELD = SYSTEM_FIELD
    IS_DEFAULT_FIELD = IS_DEFAULT_FIELD
    NAME_FIELD = NAME_FIELD
    ABBREV_FIELD = ABBREV_FIELD
    BASE_US_FIELD = BASE_US_FIELD
    BASE_METRIC_FIELD = BASE_METRIC_FIELD

    MEASURE_ATTRIB_NAME_MAX_LEN: int = 30
    MEASURE_ATTRIB_ABBREV_MAX_LEN: int = 20

    DRY_FLUID = 'df'
    WEIGHT = 'w'
    UNIT = 'u'
    TYPE_CHOICES = [
        (DRY_FLUID, 'Dry/fluid'),
        (WEIGHT, 'Weight'),
        (UNIT, 'Unit'),
    ]
    SYSTEM_US = 'us'
    SYSTEM_METRIC = 'si'
    SYSTEM_ONE = '1'
    SYSTEM_CHOICES = [
        (SYSTEM_US, 'US'),
        (SYSTEM_METRIC, 'Metric'),
        (SYSTEM_ONE, 'Dimensionless'),
    ]

    type = models.CharField(
        max_length=2,
        choices=TYPE_CHOICES,
        default=DRY_FLUID,
    )
    system = models.CharField(
        max_length=2,
        choices=SYSTEM_CHOICES,
        default=SYSTEM_US,  # since the recipes use US measures
    )
    is_default = models.BooleanField(default=False, blank=False)
    name = models.CharField(
        _('name'), max_length=MEASURE_ATTRIB_NAME_MAX_LEN, unique=True)
    abbrev = models.CharField(
        _('abbreviation'), max_length=MEASURE_ATTRIB_ABBREV_MAX_LEN)

    # Measurement values are defined in terms of a base US unit
    # (since recipe data was given in US units) and metric.
    # Dry/fluid base unit is fl. oz. and weight is oz.
    # Values taken from
    # https://en.wikipedia.org/wiki/Cooking_weights_and_measures#British_(Imperial)_measures
    # https://en.wikipedia.org/wiki/United_States_customary_units
    base_us = models.DecimalField(
        max_digits=19, decimal_places=10, default=1.0)
    base_metric = models.DecimalField(
        max_digits=19, decimal_places=10, default=1.0)

    @property
    def base_system(self) -> Decimal:
        """ Conversion factor to system base unit """
        return self.other_system(self)

    def other_system(self, measure: TypeMeasure) -> Decimal:
        """
        Conversion factor to another system base unit
        :param measure: measure for which conversion factor is needed
        :return:
        """
        # doesn't matter which base used for SYSTEM_ONE as they're the same
        return self.base_metric if measure.system == Measure.SYSTEM_METRIC \
            else self.base_us

    @dataclass
    class Meta:
        """ Model metadata """

    @classmethod
    def _get_default_instance(
            cls, name: str, abbrev: str, measure_type: str,
            system: str) -> TypeMeasure:
        """
        Get a default instance for objects requiring a Measure field
        :param name: measure name
        :param abbrev: abbreviation
        :param measure_type: type of unit
        :param system: measurement system
        :return: default instance
        """
        default_inst, _ = cls.objects.get_or_create(**{
                f'{Measure.NAME_FIELD}': name,
            },
            defaults={
                f'{Measure.TYPE_FIELD}': measure_type,
                f'{Measure.ABBREV_FIELD}': abbrev,
                f'{Measure.SYSTEM_FIELD}': system,
                f'{Measure.IS_DEFAULT_FIELD}': True,
                f'{Measure.BASE_US_FIELD}': 1.0,
                f'{Measure.BASE_METRIC_FIELD}': 1.0,
            },
        )
        return default_inst

    @classmethod
    def get_default_unit(cls) -> TypeMeasure:
        """ Get the default pk for objects requiring a Measure field """
        return cls._get_default_instance(
            'unit', '', Measure.UNIT, Measure.SYSTEM_ONE)

    @classmethod
    def get_default_us_dry_fluid(cls) -> TypeMeasure:
        """
        Get the default US base unit for objects requiring a dry/fluid
        Measure field
        """
        return cls._get_default_instance(
            'fluid ounce', 'fl. oz.', Measure.DRY_FLUID, Measure.SYSTEM_US)

    @classmethod
    def get_default_us_weight(cls) -> TypeMeasure:
        """
        Get the default US base unit for objects requiring a weight
        Measure field
        """
        return cls._get_default_instance(
            'ounce', 'oz.', Measure.WEIGHT, Measure.SYSTEM_US)

    @classmethod
    def get_default_metric_dry_fluid(cls) -> TypeMeasure:
        """
        Get the default US base unit for objects requiring a dry/fluid
        Measure field
        """
        return cls._get_default_instance(
            'decilitre', 'dl', Measure.DRY_FLUID, Measure.SYSTEM_METRIC)

    @classmethod
    def get_default_metric_weight(cls) -> TypeMeasure:
        """
        Get the default US base unit for objects requiring a weight
        Measure field
        """
        return cls._get_default_instance(
            'gram', 'g', Measure.WEIGHT, Measure.SYSTEM_METRIC)

    def __str__(self):
        return f'{self.name}'
