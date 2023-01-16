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

from profiles.models import Address
from utils import SortOrder, DESC_LOOKUP


# workaround for self type hints from https://peps.python.org/pep-0673/
TypeAddressSortOrder = \
    TypeVar("TypeAddressSortOrder", bound="AddressSortOrder")


class AddressQueryType(Enum):
    """ Enum representing different query types """
    UNKNOWN = auto()
    MY_ADDRESSES = auto()
    ALL_ADDRESSES = auto()


class AddressSortOrder(SortOrder):
    """ Enum representing addresses sort orders """
    COUNTRY_AZ = (
        'Country A-Z', 'caaz', f'{Address.COUNTRY_FIELD}')
    COUNTRY_ZA = (
        'Country Z-A', 'caza', f'{DESC_LOOKUP}{Address.COUNTRY_FIELD}')

    @classmethod
    def country_orders(cls) -> list[TypeAddressSortOrder]:
        """ List of country-related sort orders """
        return [AddressSortOrder.COUNTRY_AZ, AddressSortOrder.COUNTRY_ZA]

    @property
    def is_country_order(self) -> bool:
        """ Check if this object is a country-related sort order """
        return self in self.country_orders()

    def to_field(self) -> str:
        """ Get Address field used for sorting """
        return Address.COUNTRY_FIELD


AddressSortOrder.DEFAULT = AddressSortOrder.COUNTRY_AZ
