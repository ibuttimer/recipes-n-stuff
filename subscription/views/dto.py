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
from typing import Tuple

from base.dto import BaseDto
from order.queries import get_user_spending
from subscription.mixin import QuantiseMixin
from subscription.models import (
    Subscription, FrequencyType, FeatureType, SubscriptionFeature
)
from subscription.views.subscription_queries import get_subscription_features
from user.models import User


@dataclass
class SubscriptionDto(QuantiseMixin, BaseDto):
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
        amt = self.quantise_amount(getattr(self, Subscription.AMOUNT_FIELD))
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
class SubscriptionFeatureDto(QuantiseMixin, BaseDto):
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
                f'{str(self.quantise_amount(self.amount))} '
                f'{self.base_currency}'
            )
        if self.feature_type in FEATURE_TEXT_WITH_COUNT:
            text = text.replace(
                SubscriptionFeature.FEATURE_COUNT_TEMPLATE_MARK,
                f'{self.count}'
            )
        return text

    def order_qualifies(self, user: User, subtotal: float) -> Tuple[bool, int]:
        """
        Check if the specified user and subtotal qualify for this subscription
        feature
        :param user: user
        :param subtotal: purchase subtotal
        :return: tuple of True if qualified and remaining
                first x free deliveries
        """
        qualifies = False
        remaining_x_free = 0
        if self.feature_type in FeatureType.free_delivery_choices():

            spent, orders, first_x_free = get_user_spending(user)

            for feature, check in [
                # free delivery
                (FeatureType.FREE_DELIVERY, True),
                # free delivery over order amount
                (FeatureType.FREE_DELIVERY_OVER, subtotal > self.amount),
                # free delivery over spent amount
                (FeatureType.FREE_DELIVERY_AFTER, spent > self.amount),
                # first x free delivery deliveries
                (FeatureType.FIRST_X_FREE, first_x_free < self.count),
                # all free over spent amount
                (FeatureType.FREE_AFTER_SPEND, spent > self.amount),
            ]:
                qualifies = feature.is_from_choice(self.feature_type) and check

                if feature == FeatureType.FIRST_X_FREE:
                    remaining_x_free = self.count - first_x_free
                    if remaining_x_free < 0:
                        remaining_x_free = 0

                if qualifies:
                    break

        return qualifies, remaining_x_free

    def __str__(self):
        return f'{self.feature_type} {self.description} {self.amount} ' \
               f'{self.base_currency}/{self.count}'
