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
from django.db.models import DurationField
from django.utils.translation import gettext_lazy as _

from utils import ModelMixin

from .constants import (
    NAME_FIELD, TYPE_FIELD, ABBREV_FIELD, BASE_US_FIELD, BASE_METRIC_FIELD,
    MEASURE_FIELD
)


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

    type = models.CharField(
        max_length=2,
        choices=TYPE_CHOICES,
        default=DRY_FLUID,
    )
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
    base_us = models.DecimalField(max_digits=12, decimal_places=5)
    base_metric = models.DecimalField(max_digits=12, decimal_places=5)

    @dataclass
    class Meta:
        """ Model metadata """

    def __str__(self):
        return f'{self.name}'
