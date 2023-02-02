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
from collections import namedtuple
from dataclasses import dataclass
from enum import Enum
from typing import Optional, TypeVar, List, Tuple
from decimal import Decimal

from django.db import models
from django.utils.translation import gettext_lazy as _

from recipesnstuff.settings import DEFAULT_CURRENCY
from subscription.models import Subscription
from user.models import User
from utils import ModelMixin, NameChoiceMixin, DATE_OLDEST_LOOKUP

from .constants import (
    USER_FIELD, CREATED_FIELD, UPDATED_FIELD, STATUS_FIELD, AMOUNT_FIELD,
    BASE_CURRENCY_FIELD, ORDER_NUM_FIELD, ITEMS_FIELD,
    TYPE_FIELD, SUBSCRIPTION_FIELD, SKU_FIELD
)


# workaround for self type hints from https://peps.python.org/pep-0673/
TypeOrderStatusOption = \
    TypeVar("OrderStatusOption", bound="OrderStatusOption")
TypeProductOption = TypeVar("ProductOption", bound="ProductOption")


OrderStatusOption = namedtuple(
    'OrderStatusOption', [NameChoiceMixin.NAME, NameChoiceMixin.CHOICE])
ProductOption = namedtuple(
    'ProductOption', [NameChoiceMixin.NAME, NameChoiceMixin.CHOICE])


class OrderStatus(NameChoiceMixin, Enum):
    """ Enum representing order statuses """
    IN_PROGRESS = OrderStatusOption('In progress', 'ip')
    PENDING_PAYMENT = OrderStatusOption('Pending payment', 'pp')
    PAID = OrderStatusOption('Paid', 'p')
    PREPARING = OrderStatusOption('Preparing', 'pr')
    PENDING_SHIPPING = OrderStatusOption('Pending shipping', 'ps')
    IN_TRANSIT = OrderStatusOption('In transit', 'it')
    DELIVERED = OrderStatusOption('Delivered', 'd')
    COMPLETED = OrderStatusOption('Completed', 'cd')
    RETURN_REQUESTED = OrderStatusOption('Return requested', 'rr')
    RETURN_APPROVED = OrderStatusOption('Return approved', 'ra')
    RETURN_DENIED = OrderStatusOption('Return denied', 'rd')
    RETURN_IN_TRANSIT = OrderStatusOption('Return in transit', 'rt')
    RETURNED = OrderStatusOption('Returned', 'rn')
    VOID = OrderStatusOption('Void', 'v')
    CANCELLED = OrderStatusOption('Cancelled', 'c')

    @staticmethod
    def from_choice(choice: str) -> Optional[TypeOrderStatusOption]:
        """
        Get the OrderStatus corresponding to `choice`
        :param choice: choice to find
        :return: feature type or None of not found
        """
        return NameChoiceMixin.obj_from_choice(OrderStatus, choice)

    @staticmethod
    def get_feature_choices() -> List[Tuple]:
        """
        Get the status type choices
        :return: list of choices
        """
        return NameChoiceMixin.get_model_choices(OrderStatus)


NameChoiceMixin.assert_uniqueness(OrderStatus)


class ProductType(NameChoiceMixin, Enum):
    """ Enum representing order product types """
    MISCELLANEOUS = ProductOption('Miscellaneous', 'm')
    SUBSCRIPTION = ProductOption('Subscription', 's')
    INGREDIENT_BOX = ProductOption('Ingredient box', 'ib')
    COOKING_CLASS = ProductOption('Cooking class', 'cc')

    @staticmethod
    def from_choice(choice: str) -> Optional[TypeProductOption]:
        """
        Get the ProductOption corresponding to `choice`
        :param choice: choice to find
        :return: feature type or None of not found
        """
        return NameChoiceMixin.obj_from_choice(ProductType, choice)

    @staticmethod
    def get_feature_choices() -> List[Tuple]:
        """
        Get the status type choices
        :return: list of choices
        """
        return NameChoiceMixin.get_model_choices(ProductType)


NameChoiceMixin.assert_uniqueness(ProductType)


class OrderProduct(ModelMixin, models.Model):
    """
    Order product model
    """
    # field names
    TYPE_FIELD = TYPE_FIELD
    SUBSCRIPTION_FIELD = SUBSCRIPTION_FIELD
    SKU_FIELD = SKU_FIELD

    ORDER_PRODUCT_ATTRIB_TYPE_MAX_LEN: int = 2
    ORDER_PRODUCT_ATTRIB_SKU_MAX_LEN: int = 40

    type = models.CharField(
        _('type'), max_length=ORDER_PRODUCT_ATTRIB_TYPE_MAX_LEN,
        choices=ProductType.get_feature_choices(),
        default=ProductType.MISCELLANEOUS.choice,
    )

    subscription = models.ForeignKey(Subscription, models.SET_NULL,
                                     blank=True, null=True)

    sku = models.CharField(
        _('order number'), max_length=ORDER_PRODUCT_ATTRIB_SKU_MAX_LEN,
        blank=False, unique=True
    )

    @dataclass
    class Meta:
        """ Model metadata """
        ordering = [f'{TYPE_FIELD}']

    def __str__(self):
        return f'{self.type} {self.subscription}'


class Order(ModelMixin, models.Model):
    """
    Order model
    """
    # field names
    USER_FIELD = USER_FIELD
    CREATED_FIELD = CREATED_FIELD
    UPDATED_FIELD = UPDATED_FIELD
    STATUS_FIELD = STATUS_FIELD
    AMOUNT_FIELD = AMOUNT_FIELD
    BASE_CURRENCY_FIELD = BASE_CURRENCY_FIELD
    ORDER_NUM_FIELD = ORDER_NUM_FIELD
    ITEMS_FIELD = ITEMS_FIELD

    ORDER_ATTRIB_ORDER_NUM_MAX_LEN: int = 40
    ORDER_ATTRIB_STATUS_MAX_LEN: int = 2
    ORDER_ATTRIB_CURRENCY_CODE_MAX_LEN: int = 3

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    created = models.DateTimeField(_('created'), auto_now_add=True)
    updated = models.DateTimeField(_('updated'), auto_now=True)

    status = models.CharField(
        _('status'), max_length=ORDER_ATTRIB_STATUS_MAX_LEN,
        choices=OrderStatus.get_feature_choices(),
        default=OrderStatus.VOID.choice,
    )

    amount = models.DecimalField(
        _('amount'), default=Decimal.from_float(0), decimal_places=2,
        max_digits=19)

    base_currency = models.CharField(
        _('base currency'),
        max_length=ORDER_ATTRIB_CURRENCY_CODE_MAX_LEN, blank=False,
        default=DEFAULT_CURRENCY.upper())

    order_num = models.CharField(
        _('order number'), max_length=ORDER_ATTRIB_ORDER_NUM_MAX_LEN,
        blank=False
    )

    items = models.ManyToManyField(OrderProduct)

    @dataclass
    class Meta:
        """ Model metadata """
        ordering = [f'{DATE_OLDEST_LOOKUP}{CREATED_FIELD}']

    def __str__(self):
        return f'{self.order_num} {self.created} {str(self.user)}'
