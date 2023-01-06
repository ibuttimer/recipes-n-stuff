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

from django import forms
from django_countries.widgets import CountrySelectWidget

from utils import FormMixin

from .constants import (
    COUNTRY_FIELD, STREET_FIELD,
    STREET2_FIELD, CITY_FIELD, STATE_FIELD, POSTCODE_FIELD,
    IS_DEFAULT_FIELD
)
from .models import Address


class AddressForm(FormMixin, forms.ModelForm):
    """ Address form """

    COUNTRY_FIELD_FF = COUNTRY_FIELD
    STREET_FIELD_FF = STREET_FIELD
    STREET2_FIELD_FF = STREET2_FIELD
    CITY_FIELD_FF = CITY_FIELD
    STATE_FIELD_FF = STATE_FIELD
    POSTCODE_FIELD_FF = POSTCODE_FIELD
    IS_DEFAULT_FIELD_FF = IS_DEFAULT_FIELD

    @dataclass
    class Meta:
        """ Form metadata """
        model = Address
        fields = [
            COUNTRY_FIELD, STREET_FIELD,
            STREET2_FIELD, CITY_FIELD, STATE_FIELD, POSTCODE_FIELD,
            IS_DEFAULT_FIELD
        ]
        bool_fields = [
            IS_DEFAULT_FIELD
        ]
        widgets = {
            # https://pypi.org/project/django-countries/#countryselectwidget
            COUNTRY_FIELD: CountrySelectWidget(
                layout='{widget}<img class="country-select-flag" '
                       'id="{flag_id}" src="{country.flag}">'
            )
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # add the bootstrap class to the widget
        self.add_form_control(
            AddressForm.Meta.fields, exclude=AddressForm.Meta.bool_fields)
        self.add_form_check_input(AddressForm.Meta.bool_fields)
