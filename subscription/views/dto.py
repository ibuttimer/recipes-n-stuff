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
from subscription.forms import SubscriptionForm
from subscription.models import (
    Subscription, FrequencyType, FeatureType, SubscriptionFeature
)
from subscription.views.subscription_queries import get_subscription_features


@dataclass
class SubscriptionDto(BaseDto):
    """ Subscription data transfer object """

    @staticmethod
    def from_model(subscription: Subscription, with_features: bool = True):
        """
        Generate a DTO from the specified `model`
        :param subscription: model instance to populate DTO from
        :param with_features: include features flag
        :return: DTO instance
        """
        dto = BaseDto.from_model_to_obj(subscription, SubscriptionDto())
        # custom handling for specific attributes
        dto.frequency_type = \
            FrequencyType.from_choice(subscription.frequency_type)

        if with_features:
            features = get_subscription_features(dto.id)
            dto.features = list(
                map(SubscriptionFeatureDto.from_model, features)
            )

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
        freq_type = getattr(self, Subscription.FREQUENCY_TYPE_FIELD)
        freq = getattr(self, Subscription.FREQUENCY_FIELD)
        assert freq_type is not None
        order.append(f'{amt} {code} per {freq} {freq_type.value.name}')

        return order


FEATURE_DESC_AS_TEXT = [
    FeatureType.BASIC.value.choice, FeatureType.FREE_DELIVERY.value.choice,
    FeatureType.FREE_CLASSES.value.choice
]
FEATURE_TEXT_WITH_AMOUNT = [
    FeatureType.FREE_DELIVERY_OVER.value.choice,
    FeatureType.FREE_DELIVERY_AFTER.value.choice,
    FeatureType.FREE_AFTER_SPEND.value.choice
]
FEATURE_TEXT_WITH_COUNT = [
    FeatureType.FIRST_X_FREE.value.choice
]


@dataclass
class SubscriptionFeatureDto(BaseDto):
    """ SubscriptionFeature data transfer object """

    @staticmethod
    def from_model(feature: SubscriptionFeature):
        """
        Generate a DTO from the specified `model`
        :param feature: model instance to populate DTO from
        :return: DTO instance
        """
        return BaseDto.from_model_to_obj(feature, SubscriptionFeatureDto())

    @property
    def display_text(self) -> str:
        """
        Get display text for feature
        :return: display text
        """
        text = self.description
        # default is sufficient for FEATURE_DESC_AS_TEXT

        if self.feature_type in FEATURE_TEXT_WITH_AMOUNT:
            text = text.replace(
                SubscriptionFeature.FEATURE_AMOUNT_TEMPLATE_MARK,
                f'{str(SubscriptionForm.quantise_amount(self.amount))} '
                f'{self.base_currency}'
            )
        if self.feature_type in FEATURE_TEXT_WITH_COUNT:
            text = text.replace(
                SubscriptionFeature.FEATURE_COUNT_TEMPLATE_MARK,
                f'{self.count}'
            )
        return text
