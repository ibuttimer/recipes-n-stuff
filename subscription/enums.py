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
from .models import Subscription


# workaround for self type hints from https://peps.python.org/pep-0673/
TypeSubscriptionSortOrder = \
    TypeVar("TypeSubscriptionSortOrder", bound="SubscriptionSortOrder")


class SubscriptionQueryType(Enum):
    """ Enum representing different query types """
    UNKNOWN = auto()
    ALL_SUBSCRIPTIONS = auto()


class SubscriptionSortOrder(SortOrder):
    """ Enum representing addresses sort orders """
    NAME_AZ = (
        'Name A-Z', 'naz', f'{Subscription.NAME_FIELD}')
    NAME_ZA = (
        'Name Z-A', 'nza', f'{DESC_LOOKUP}{Subscription.NAME_FIELD}')
    COST_LH = (
        'Cost Low-High', 'caz', f'{Subscription.AMOUNT_FIELD}')
    COST_HL = (
        'Cost High-Low', 'cza', f'{DESC_LOOKUP}{Subscription.AMOUNT_FIELD}')

    @classmethod
    def name_orders(cls) -> list[TypeSubscriptionSortOrder]:
        """ List of name-related sort orders """
        return [SubscriptionSortOrder.NAME_AZ, SubscriptionSortOrder.NAME_ZA]

    @property
    def is_name_order(self) -> bool:
        """ Check if this object is a name-related sort order """
        return self in self.name_orders()

    def to_field(self) -> str:
        """ Get Subscription field used for sorting """
        return Subscription.NAME_FIELD


SubscriptionSortOrder.DEFAULT = SubscriptionSortOrder.NAME_AZ
