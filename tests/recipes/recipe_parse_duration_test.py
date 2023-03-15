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
from datetime import timedelta
from typing import Tuple, List
from unittest import TestCase

import pytest
from more_itertools import distinct_permutations

from recipes.views.utils import (
    YEAR, MTH, WK, DAY, HOUR, MIN, SEC, parse_duration
)

ALL_SYMBOLS = [YEAR, MTH, WK, DAY, HOUR, MIN, SEC]


class TestParseDuration(unittest.TestCase):

    def check_symbol_decode_success(
            self, num: int, symbol: str, expected: timedelta):

        str_set = self.pass_set(num, symbol.lower())         # lowercase
        str_set.extend(self.pass_set(num, symbol.upper()))   # uppercase
        for idx in range(1, len(symbol)):
            # mixed case
            mc_sym = symbol.replace(symbol[idx], symbol[idx].upper())
            str_set.extend(self.pass_set(num, mc_sym))

        for dur_str in str_set:
            with self.subTest(f"check_symbol_decode; {num} {symbol}",
                              dur_str=dur_str):
                self.assert_true(dur_str, expected)

    @staticmethod
    def pass_set(n: int, sym: str):
        return [
            f'{n}{sym}', f' {n}{sym}', f' {n}{sym} ', f' {n} {sym} ',
        ]

    def check_multi_symbol_decode_success(
            self, vals: List[Tuple[int, str]], expected: timedelta):

        sets = list(map(
            lambda val: self.pass_set(*val), vals
        ))

        for start_idx in range(0, len(sets)):   # idx of 1st set
            start_set = sets[start_idx]
            for t_idx in range(0, len(start_set)):    # idx of term in set
                # generate duration string with term from start_set as start
                # with terms for other sets appended
                dur_str = start_set[t_idx]
                dur_str += ' ' + ' '.join([
                    o_set[t_idx] for c_idx, o_set in enumerate(sets)
                    if c_idx != start_idx
                ])

                with self.subTest(f"check_symbol_decode; {dur_str}",
                                  dur_str=dur_str):
                    self.assert_true(dur_str, expected)

    def assert_true(self, dur: str, expected: timedelta):
        is_valid, duration = parse_duration(dur)
        self.assertTrue(is_valid, f'"{dur}" expected True')
        self.assertEqual(
            expected, duration,
            f'"{dur}" expected equal {expected} {duration}')

    def check_symbol_decode_fail(self, num: int, symbol: str):
        def fail_set(n: int, sym: str):
            return [
                f'{sym}{n}', f' {sym}{n}', f' {sym}{n} ', f' {sym} {n} ',
                f'{sym}.0{n}', f' {sym}-{n}', f' {sym}={n} ', f' {sym}=={n} ',
                f' {sym}:{n} ',
                f'-{n}{sym}', f'0.{n}{sym}', f'.{n}{sym}', f'{n}/1 {sym}'
            ]

        str_set = fail_set(num, symbol.lower())         # lowercase
        str_set.extend(fail_set(num, symbol.upper()))   # uppercase
        for idx in range(1, len(symbol)):
            # mixed case
            mc_sym = symbol.replace(symbol[idx], symbol[idx].upper())
            str_set.extend(fail_set(num, mc_sym))

        for dur_str in str_set:
            with self.subTest(f"check_symbol_decode; {num} {symbol}",
                              dur_str=dur_str):
                self.assert_false(dur_str)

    def assert_false(self, dur: str):
        is_valid, duration = parse_duration(dur)
        self.assertFalse(is_valid, f'"{dur}" expected False')
        self.assertIsNone(duration, f'"{dur}" expected None')

    @staticmethod
    def calc_timedelta(num, symbol):
        factor = 365 if symbol == YEAR else \
            31 if symbol == MTH else 1
        key = 'days' if symbol in [YEAR, MTH, DAY] else \
            'weeks' if symbol == WK else \
            'hours' if symbol == HOUR else \
            'minutes' if symbol == MIN else 'seconds'
        return timedelta(**{
            key: num * factor
        })

    def test_parse_duration(self):
        """ Test duration parsing """
        for num in range(0, 2):
            for symbol in ALL_SYMBOLS:
                self.check_symbol_decode_success(
                    num, symbol, self.calc_timedelta(num, symbol))

                self.check_symbol_decode_fail(num, symbol)

        # test combos of 2
        for num0 in range(0, 2):
            for num1 in range(0, 2):
                for sym_idx0 in range(0, len(ALL_SYMBOLS) - 1):
                    vals = [(num0, ALL_SYMBOLS[sym_idx0])]
                    for sym_idx1 in range(sym_idx0 + 1, len(ALL_SYMBOLS)):
                        expected = self.calc_timedelta(
                            num0, ALL_SYMBOLS[sym_idx0])
                        expected += self.calc_timedelta(
                            num1, ALL_SYMBOLS[sym_idx1])

                        vals = vals[:1] + [(num1, ALL_SYMBOLS[sym_idx1])]

                        self.check_multi_symbol_decode_success(
                            vals, expected)

        # test permutations of all symbols, with same expected result
        nums = [n + 1 for n in range(len(ALL_SYMBOLS))]
        expected = timedelta()
        for idx in range(len(nums)):
            expected += self.calc_timedelta(nums[idx], ALL_SYMBOLS[idx])

        for perm in distinct_permutations(range(len(ALL_SYMBOLS))):
            vals = []
            for idx in range(len(perm)):
                vals.append((nums[idx], ALL_SYMBOLS[idx]))

            self.check_multi_symbol_decode_success(vals, expected)
