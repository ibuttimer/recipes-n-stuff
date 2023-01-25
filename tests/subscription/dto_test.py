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

from recipesnstuff.constants import SUBSCRIPTION_APP_NAME
from subscription.dto import SubscriptionDto
from subscription.constants import (
    NAME_FIELD, DESCRIPTION_FIELD, FREQUENCY_TYPE_FIELD, FREQUENCY_FIELD,
    BASE_CURRENCY_FIELD, AMOUNT_FIELD, IS_ACTIVE_FIELD
)

# excluding country order
DISPLAY_ORDER = [
    NAME_FIELD, DESCRIPTION_FIELD, FREQUENCY_TYPE_FIELD, FREQUENCY_FIELD,
    BASE_CURRENCY_FIELD, AMOUNT_FIELD, IS_ACTIVE_FIELD
]


@pytest.mark.django_db
class TestSubscriptionDto(unittest.TestCase):
    """
    Test SubscriptionDto class
    https://docs.pytest.org/
    https://pypi.org/project/mixer/
    """

    @classmethod
    def setUpClass(cls):
        """ Setup test """
        cls.dto_new = SubscriptionDto.add_new_obj()

    def setUp(self):
        """ Setup test """
        self.subscription = mixer.blend(f'{SUBSCRIPTION_APP_NAME}.Subscription')
        self.dto = SubscriptionDto.from_model(self.subscription)

    def test_display_order(self):
        """ Test display order """
        self.assertEqual(
            self.dto.display_order, [
                getattr(self.subscription, key) for key in DISPLAY_ORDER
            ])

    def test_add_new(self):
        """ Test add new placeholder """
        self.assertTrue(self.dto_new.add_new)
        self.assertFalse(self.dto.add_new)


if __name__ == '__main__':
    unittest.main()
