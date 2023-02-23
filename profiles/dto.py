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
from dataclasses import dataclass

from base.dto import BaseDto
from profiles.models import Address


@dataclass
class AddressDto(BaseDto):
    """ Address data transfer object """

    is_selected: bool = False

    @staticmethod
    def from_model(address: Address, is_selected: bool = False):
        """
        Generate a DTO from the specified `model`
        :param address: model instance to populate DTO from
        :param is_selected: is selected state: default False
        :return: DTO instance
        """
        dto = BaseDto.from_model_to_obj(address, AddressDto())
        # custom handling for specific attributes
        dto.is_selected = is_selected
        return dto

    @staticmethod
    def add_new_obj():
        """
        Generate add new placeholder a DTO
        :return: DTO instance
        """
        return BaseDto.to_add_new_obj(AddressDto())

    @property
    def display_order_ex_country(self):
        """ Field values in display order (excluding country) """
        return [
            getattr(self, key) for key in [
                Address.STREET_FIELD, Address.STREET2_FIELD,
                Address.CITY_FIELD, Address.STATE_FIELD,
                Address.POSTCODE_FIELD
            ]
        ]

    @property
    def display_order(self):
        """ Field values in display order """
        fields = self.display_order_ex_country
        fields.append(getattr(self, Address.COUNTRY_FIELD))
        return fields

    def __str__(self):
        return f'{self.street} {self.country} {str(self.user)}'
