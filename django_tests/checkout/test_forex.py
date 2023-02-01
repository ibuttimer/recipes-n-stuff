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
from decimal import Decimal
from unittest import mock

from checkout.forex import convert_forex, NumType
from recipesnstuff.settings import DEFAULT_CURRENCY

from .base_checkout_test_cls import BaseCheckoutTest


class TestForexFixtures(BaseCheckoutTest):
    """
    Test measure model
    https://docs.djangoproject.com/en/4.1/topics/testing/tools/
    """

    @mock.patch('checkout.forex.datetime')
    def test_forex_conversion(self, mocked_datetime):
        """ Test forex conversions """

        # timestamp half default interval before test rates timestamp
        mocked_datetime.now.return_value = self.test_timestamp

        for units in range(2):
            for code in self.test_rates:
                if code == DEFAULT_CURRENCY:
                    continue
                with self.subTest(
                        f'default: smallest unit False, result as float, '
                        f'count {units}',
                        code=code, count=units):
                    self.assertEqual(
                        round(self.test_rates[code] * units,
                              self.test_digits[code]),
                        convert_forex(1, 'EUR', code, count=units)
                    )

        for units in range(2):
            for code in self.test_rates:
                if code == DEFAULT_CURRENCY:
                    continue
                with self.subTest(
                        f'smallest unit True, count {units}',
                        code=code, count=units):
                    self.assertEqual(
                        int(self.test_rates[code] * units *
                            (10 ** self.test_digits[code])
                        ),
                        convert_forex(1, 'EUR', code, count=units,
                                      smallest_unit=True)
                    )

        for units in range(2):
            for code in self.test_rates:
                if code == DEFAULT_CURRENCY:
                    continue
                with self.subTest(
                        f'smallest unit False, result as float, '
                        f'count {units}',
                        code=code, count=units):
                    self.assertEqual(
                        Decimal.from_float(
                            self.test_rates[code] * units
                        ).quantize(Decimal('10') ** -self.test_digits[code]),
                        convert_forex(1, 'EUR', code, count=units,
                                      smallest_unit=False,
                                      result_as=NumType.DECIMAL)
                    )
