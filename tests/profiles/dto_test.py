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

import unittest
import pytest
from mixer.backend.django import mixer

from profiles.dto import AddressDto
from profiles.constants import (
    COUNTRY_FIELD, STREET_FIELD, STREET2_FIELD, CITY_FIELD, STATE_FIELD,
    POSTCODE_FIELD, IS_DEFAULT_FIELD
)

# excluding country order
EX_COUNTRY_ORDER = [
    STREET_FIELD, STREET2_FIELD, CITY_FIELD,
    STATE_FIELD, POSTCODE_FIELD
]
# including country order
INC_COUNTRY_ORDER = EX_COUNTRY_ORDER.copy()
INC_COUNTRY_ORDER.append(COUNTRY_FIELD)

@pytest.mark.django_db
class TestAddressDto(unittest.TestCase):
    """
    Test AddressDto class
    https://docs.pytest.org/
    https://pypi.org/project/mixer/
    """

    @classmethod
    def setUpClass(cls):
        """ Setup test """
        cls.dto_new = AddressDto.add_new_obj()

    def setUp(self):
        """ Setup test """
        self.address = mixer.blend('profiles.Address')
        self.dto = AddressDto.from_model(self.address)

    def test_display_order_ex_country(self):
        """ Test display order excluding country """
        self.assertEqual(
            self.dto.display_order_ex_country, [
                getattr(self.address, key) for key in EX_COUNTRY_ORDER
            ])

    def test_display_order(self):
        """ Test display order including country """
        self.assertEqual(
            self.dto.display_order, [
                getattr(self.address, key) for key in INC_COUNTRY_ORDER
        ])

    def test_add_new(self):
        """ Test add new placeholder """
        self.assertTrue(self.dto_new.add_new)
        self.assertFalse(self.dto.add_new)


if __name__ == '__main__':
    unittest.main()
