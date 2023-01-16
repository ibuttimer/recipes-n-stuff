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
from unittest import skip

from django.test import TestCase

from profiles.forms import AddressForm


class TestAddressForm(TestCase):
    """
    Test category
    https://docs.djangoproject.com/en/4.1/topics/testing/tools/
    """

    def test_required_fields(self):
        """ Test form not valid without all required fields """
        for country in ("", "IE"):
            for street in ("", "Street"):
                with self.subTest(country=country, street=street):
                    form = AddressForm({
                        AddressForm.COUNTRY_FIELD_FF: country,
                        AddressForm.STREET_FIELD_FF: street,
                    })
                    if country and street:
                        self.assertTrue(form.is_valid())
                    else:
                        self.assertFalse(form.is_valid())
                        field = AddressForm.STREET_FIELD_FF if not street \
                            else AddressForm.COUNTRY_FIELD_FF
                        self.assertIn(field, form.errors.keys())
                        self.assertEqual(form.errors[field][0],
                                         'This field is required.')

    def test_non_required_fields(self):
        """ Test form valid without all non-required fields """
        for street2 in ("", "Street2"):
            for city in ("", "City"):
                for state in ("", "State"):
                    for postcode in ("", "Postcode"):
                        with self.subTest(
                                street2=street2, city=city,
                                state=state, postcode=postcode):
                            form = AddressForm({
                                AddressForm.COUNTRY_FIELD_FF: "IE",
                                AddressForm.STREET_FIELD_FF: "Street",
                                AddressForm.STREET2_FIELD_FF: street2,
                                AddressForm.CITY_FIELD_FF: city,
                                AddressForm.STATE_FIELD_FF: state,
                                AddressForm.POSTCODE_FIELD_FF: postcode,
                            })
                            self.assertTrue(form.is_valid())

    def test_metaclass_fields(self):
        """ Test fields are explicit in form metaclass """
        form = AddressForm()
        self.assertEqual(form.Meta.fields, [
            AddressForm.COUNTRY_FIELD_FF, AddressForm.STREET_FIELD_FF,
            AddressForm.STREET2_FIELD_FF, AddressForm.CITY_FIELD_FF,
            AddressForm.STATE_FIELD_FF, AddressForm.POSTCODE_FIELD_FF,
            AddressForm.IS_DEFAULT_FIELD_FF
        ])
