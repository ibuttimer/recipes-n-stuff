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

from checkout.forex import convert_forex, NumType, normalise_amount
from recipesnstuff.settings import DEFAULT_CURRENCY

from .base_checkout_test_cls import BaseCheckoutTest
from checkout.basket import Basket


@mock.patch('checkout.forex.datetime')
class TestForexFixtures(BaseCheckoutTest):
    """
    Test measure model
    https://docs.djangoproject.com/en/4.1/topics/testing/tools/
    """

    def test_basket_attributes(self, mocked_datetime):
        """ Test basket attributes """

        # timestamp half default interval before test rates timestamp
        mocked_datetime.now.return_value = self.test_timestamp

        basket = Basket()

        # check defaults
        with self.subTest('defaults'):
            self.verify_basket_attributes(basket, 0, DEFAULT_CURRENCY, 0)

        index = self.codes.index(DEFAULT_CURRENCY.upper())
        index = index + 1 if index == 0 else -1
        basket.currency = self.codes[index]

        with self.subTest('non-default currency', currency=self.codes[index]):
            self.verify_basket_attributes(basket, 0, self.codes[index], 0)

    def verify_basket_attributes(
            self, basket: Basket, total: float = None, currency: str = None,
            items: int = None, payment_total: int = None):
        """ Verify basket attributes """
        if total is not None:
            self.assertEqual(
                basket.total,
                float(total) if isinstance(total, Decimal) else total)
        if payment_total is not None:
            self.assertEqual(
                basket.payment_total,
                int(payment_total) if isinstance(payment_total, Decimal)
                else payment_total)
        if currency is not None:
            self.assertEqual(basket.currency.lower(), currency.lower())
        if items is not None:
            self.assertEqual(basket.num_items, items)

    def test_basket_total(self, mocked_datetime):
        """ Test forex conversions """

        # timestamp half default interval before test rates timestamp
        mocked_datetime.now.return_value = self.test_timestamp

        basket = Basket()

        with self.subTest('multiple same cost items'):
            expected_total = 0
            expected_items = 0
            for idx in range(1, 5):
                basket.add(1, f'item {idx}')
                expected_total += 1
                expected_items += 1
            self.verify_basket_attributes(
                basket, total=expected_total, items=expected_items)

        with self.subTest('basket clear'):
            currency = basket.currency
            basket.clear()
            self.verify_basket_attributes(basket, 0, currency, 0)

        with self.subTest('multiple different cost items'):
            expected_total = 0
            expected_items = 0
            for idx in range(1, 5):
                basket.add(idx, f'item {idx}')
                expected_total += idx
                expected_items += 1
            self.verify_basket_attributes(
                basket, total=expected_total, items=expected_items)

        basket.clear()
        self.verify_basket_attributes(basket, 0, currency, 0)

        with self.subTest('multiple different cost/count items'):
            expected_total = 0
            expected_items = 0
            for idx in range(1, 5):
                basket.add(idx, f'item {idx}', count=idx)
                expected_total += (idx * idx)
                expected_items += 1
            self.verify_basket_attributes(
                basket, total=expected_total, items=expected_items)

        basket.clear()
        self.verify_basket_attributes(basket, 0, currency, 0)

        items = [
            # cost, currency, total
            (idx,
             code,
             (Decimal.from_float(
                 self.test_rates[basket.currency]) / Decimal.from_float(
                 self.test_rates[code])
              ) * idx
             )
            for idx, code in enumerate(self.codes)
        ]

        with self.subTest('multiple different currency items'):
            expected_total = Decimal(0)
            expected_items = 0
            for idx in range(1, 5):
                basket.add(items[idx][0], f'item {idx}', currency=items[idx][1])
                expected_total += items[idx][2]
                expected_items += 1
            self.verify_basket_attributes(
                basket,
                total=normalise_amount(
                    expected_total, basket.currency, result_as=NumType.DECIMAL
                ),
                items=expected_items,
                payment_total=normalise_amount(
                    expected_total, basket.currency, smallest_unit=True
                )
            )
