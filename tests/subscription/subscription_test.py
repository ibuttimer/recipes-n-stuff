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
from copy import copy
from datetime import datetime

import pytest
from pytest_subtests import subtests

from subscription.models import FrequencyType


class TestFrequencyType(unittest.TestCase):
    """
    Test FrequencyType class
    https://docs.pytest.org/
    """

    def test_timedelta(self):
        """ Test timedelta """

        test_date = datetime(year=2023, month=1, day=27, hour=10, minute=56)
        inc_amt = 2

        expected_date = test_date.replace(minute=test_date.minute + inc_amt)
        self.assertEqual(expected_date,
                         test_date + FrequencyType.BY_MIN.timedelta(inc_amt))
        expected_date = test_date.replace(hour=test_date.hour + inc_amt)
        self.assertEqual(expected_date,
                         test_date + FrequencyType.HOURLY.timedelta(inc_amt))
        expected_date = test_date.replace(day=test_date.day + inc_amt)
        self.assertEqual(expected_date,
                         test_date + FrequencyType.DAILY.timedelta(inc_amt))
        expected_date = test_date.replace(month=test_date.month + inc_amt)
        self.assertEqual(expected_date,
                         test_date + FrequencyType.MONTHLY.timedelta(inc_amt))
        expected_date = test_date.replace(year=test_date.year + inc_amt)
        self.assertEqual(expected_date,
                         test_date + FrequencyType.YEARLY.timedelta(inc_amt))


if __name__ == '__main__':
    unittest.main()
