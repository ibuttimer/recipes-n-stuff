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
from .forms import SubscriptionForm
from .models import Subscription, FrequencyType


@dataclass
class SubscriptionDto(BaseDto):
    """ Subscription data transfer object """

    @staticmethod
    def from_model(address: Subscription):
        """
        Generate a DTO from the specified `model`
        :param address: model instance to populate DTO from
        :return: DTO instance
        """
        dto = BaseDto.from_model_to_obj(address, SubscriptionDto())
        # custom handling for specific attributes
        return dto

    @staticmethod
    def add_new_obj():
        """
        Generate add new placeholder a DTO
        :return: DTO instance
        """
        return BaseDto.to_add_new_obj(SubscriptionDto())

    @property
    def display_order(self):
        """ Field values in display order """
        order = [
            getattr(self, key) for key in [
                Subscription.NAME_FIELD, Subscription.DESCRIPTION_FIELD,
            ]
        ]
        amt = SubscriptionForm.quantise_amount(
            getattr(self, Subscription.AMOUNT_FIELD))
        code = getattr(self, Subscription.BASE_CURRENCY_FIELD)
        freq_type =  FrequencyType.from_choice(
            getattr(self, Subscription.FREQUENCY_TYPE_FIELD)
        )
        freq = getattr(self, Subscription.FREQUENCY_FIELD)
        assert freq_type is not None
        order.append(f'{amt} {code} per {freq} {freq_type.value.name}')

        return order
