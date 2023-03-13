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
from enum import auto, Enum
from typing import TypeVar

from utils import SortOrder, DESC_LOOKUP
from .models import Order

# workaround for self type hints from https://peps.python.org/pep-0673/
TypeOrderSortOrder = \
    TypeVar("TypeOrderSortOrder", bound="OrderSortOrder")


class OrderQueryType(Enum):
    """ Enum representing different order query types """
    UNKNOWN = auto()
    ALL_ORDERS = auto()


UP_ARROWS = "\N{North East Arrow}"
DOWN_ARROWS = "\N{South East Arrow}"


class OrderSortOrder(SortOrder):
    """ Enum representing order sort orders """
    DATE_LH = (
        f'Date {UP_ARROWS}', 'd09', f'{Order.UPDATED_FIELD}')
    DATE_HL = (
        f'Date {DOWN_ARROWS}', 'd90', f'{DESC_LOOKUP}{Order.UPDATED_FIELD}')
    AMOUNT_LH = (
        f'Amount {UP_ARROWS}', 'a09', f'{Order.AMOUNT_FIELD}')
    AMOUNT_HL = (
        f'Amount {DOWN_ARROWS}', 'a90', f'{DESC_LOOKUP}{Order.AMOUNT_FIELD}')

    @classmethod
    def date_orders(cls) -> list[TypeOrderSortOrder]:
        """ List of date-related sort orders """
        return [OrderSortOrder.DATE_LH, OrderSortOrder.DATE_HL]

    @property
    def is_date_order(self) -> bool:
        """ Check if this object is a date-related sort order """
        return self in self.date_orders()

    @classmethod
    def amount_orders(cls) -> list[TypeOrderSortOrder]:
        """ List of amount-related sort orders """
        return [OrderSortOrder.DATE_LH, OrderSortOrder.DATE_HL]

    @property
    def is_amount_order(self) -> bool:
        """ Check if this object is an amount-related sort order """
        return self in self.amount_orders()

    def to_field(self) -> str:
        """ Get Order field used for sorting """
        return Order.UPDATED_FIELD if self in self.date_orders() else \
            Order.AMOUNT_FIELD if self in self.amount_orders() else \
            None


OrderSortOrder.DEFAULT = OrderSortOrder.DATE_HL
