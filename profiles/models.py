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

from django_countries.fields import CountryField

from user.models import User
from utils import ModelMixin

from .constants import (
    COUNTRY_FIELD, SUBDIVISION_FIELD, USER_FIELD, STREET_FIELD,
    STREET2_FIELD, CITY_FIELD, STATE_FIELD, POSTCODE_FIELD,
    IS_DEFAULT_FIELD
)


class CountryInfo(ModelMixin, models.Model):
    """
    Country information model
    """
    # field names
    COUNTRY_FIELD = COUNTRY_FIELD
    SUBDIVISION_FIELD = SUBDIVISION_FIELD

    COUNTRYINFO_ATTRIB_SUBDIV_MAX_LEN: int = 50

    country = CountryField()

    subdivision = models.CharField(
        _('subdivision'), max_length=COUNTRYINFO_ATTRIB_SUBDIV_MAX_LEN,
        blank=True)

    @dataclass
    class Meta:
        """ Model metadata """

    def __str__(self):
        return f'{self.country.name} {self.subdivision}'


class Address(ModelMixin, models.Model):
    """
    Address model
    """
    # field names
    USER_FIELD = USER_FIELD
    COUNTRY_FIELD = COUNTRY_FIELD
    STREET_FIELD = STREET_FIELD
    STREET2_FIELD = STREET2_FIELD
    CITY_FIELD = CITY_FIELD
    STATE_FIELD = STATE_FIELD
    POSTCODE_FIELD = POSTCODE_FIELD
    IS_DEFAULT_FIELD = IS_DEFAULT_FIELD

    ADDRESS_ATTRIB_STREET_MAX_LEN: int = 150
    ADDRESS_ATTRIB_STREET2_MAX_LEN: int = 150
    ADDRESS_ATTRIB_CITY_MAX_LEN: int = 50
    ADDRESS_ATTRIB_STATE_MAX_LEN: int = 50
    ADDRESS_ATTRIB_POSTCODE_MAX_LEN: int = 50

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    country = CountryField(blank_label='(Select country)')

    street = models.CharField(
        _('street address'), max_length=ADDRESS_ATTRIB_STREET_MAX_LEN,
        blank=False)
    street2 = models.CharField(
        _('street address line 2'), max_length=ADDRESS_ATTRIB_STREET2_MAX_LEN,
        blank=True)
    city = models.CharField(
        _('city'), max_length=ADDRESS_ATTRIB_CITY_MAX_LEN,
        blank=True)
    state = models.CharField(
        _('state'), max_length=ADDRESS_ATTRIB_STATE_MAX_LEN,
        blank=True)
    postcode = models.CharField(
        _('postcode'), max_length=ADDRESS_ATTRIB_POSTCODE_MAX_LEN,
        blank=True)
    is_default = models.BooleanField(
        _('default'), default=False, blank=False, help_text=_(
            "Designates that this record represents the user's "
            "default address."
        ))

    @dataclass
    class Meta:
        """ Model metadata """
        ordering = [f'-{IS_DEFAULT_FIELD}']

    def __str__(self):
        return f'{self.street} {self.country} {str(self.user)}'
