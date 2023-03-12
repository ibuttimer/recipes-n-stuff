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
from django_countries.fields import CountryField

from profiles.models import Address
from recipes.models import Recipe
from recipesnstuff.settings import (
    DEFAULT_CURRENCY, PRICING_FACTOR, PRICING_PLACES
)
from subscription.models import Subscription
from user.models import User
from utils import ModelMixin, NameChoiceMixin, DATE_OLDEST_LOOKUP
from checkout.constants import CURRENCY_CODE_MAX_LEN

from .constants import (
    USER_FIELD, CREATED_FIELD, UPDATED_FIELD, STATUS_FIELD, AMOUNT_FIELD,
    BASE_CURRENCY_FIELD, AMOUNT_BASE_FIELD, ORDER_NUM_FIELD, ITEMS_FIELD,
    TYPE_FIELD, SUBSCRIPTION_FIELD, RECIPE_FIELD, UNIT_PRICE_FIELD, SKU_FIELD,
    DESCRIPTION_FIELD, COUNTRY_FIELD, WAS_1ST_X_FREE_FIELD, INFO_FIELD,
    ORDER_FIELD, ORDER_PROD_FIELD, QUANTITY_FIELD, ADDRESS_FIELD
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
    PROCESSING_PAYMENT = OrderStatusOption('Processing payment', '@p')
    PAYMENT_FAILED = OrderStatusOption('Payment failed', 'pf')
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
    FREE_DELIVERY = ProductOption('Free delivery', 'd0')
    STANDARD_DELIVERY = ProductOption('Standard delivery', 'd1')
    PREMIUM_DELIVERY = ProductOption('Premium delivery', 'd2')

    @classmethod
    def miscellaneous_options(cls):
        return [ProductType.MISCELLANEOUS]

    @classmethod
    def subscription_options(cls):
        return [ProductType.SUBSCRIPTION]

    @classmethod
    def ingredient_box_options(cls):
        return [ProductType.INGREDIENT_BOX]

    @classmethod
    def cooking_class_options(cls):
        return [ProductType.COOKING_CLASS]

    @classmethod
    def recipe_options(cls):
        options = cls.ingredient_box_options()
        options.extend(cls.cooking_class_options())
        return options

    @classmethod
    def delivery_options(cls):
        return [
            ProductType.FREE_DELIVERY, ProductType.STANDARD_DELIVERY,
            ProductType.PREMIUM_DELIVERY
        ]

    @property
    def is_miscellaneous_option(self):
        return self in self.miscellaneous_options()

    @property
    def is_subscription_option(self):
        return self in self.subscription_options()

    @property
    def is_ingredient_box_option(self):
        return self in self.ingredient_box_options()

    @property
    def is_cooking_class_option(self):
        return self in self.cooking_class_options()

    @property
    def is_recipe_option(self):
        return self in self.recipe_options()

    @property
    def is_delivery_option(self):
        return self in self.delivery_options()

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
    RECIPE_FIELD = RECIPE_FIELD
    COUNTRY_FIELD = COUNTRY_FIELD
    UNIT_PRICE_FIELD = UNIT_PRICE_FIELD
    BASE_CURRENCY_FIELD = BASE_CURRENCY_FIELD
    DESCRIPTION_FIELD = DESCRIPTION_FIELD
    SKU_FIELD = SKU_FIELD

    COMMON_FIELDS = [
        TYPE_FIELD, SUBSCRIPTION_FIELD, UNIT_PRICE_FIELD, BASE_CURRENCY_FIELD,
        DESCRIPTION_FIELD, SKU_FIELD
    ]
    MISCELLANEOUS_FIELDS = COMMON_FIELDS
    SUBSCRIPTION_FIELDS = COMMON_FIELDS.copy()
    SUBSCRIPTION_FIELDS.append(SUBSCRIPTION_FIELD)
    INGREDIENT_BOX_FIELDS = COMMON_FIELDS.copy()
    INGREDIENT_BOX_FIELDS.append(RECIPE_FIELD)
    COOKING_CLASS_FIELDS = INGREDIENT_BOX_FIELDS
    DELIVERY_FIELDS = COMMON_FIELDS.copy()
    DELIVERY_FIELDS.append(COUNTRY_FIELD)

    ORDER_PRODUCT_ATTRIB_TYPE_MAX_LEN: int = 2
    ORDER_PRODUCT_ATTRIB_SKU_MAX_LEN: int = 40
    ORDER_PRODUCT_ATTRIB_DESC_MAX_LEN: int = 150
    ORDER_PRODUCT_ATTRIB_CURRENCY_CODE_MAX_LEN: int = CURRENCY_CODE_MAX_LEN

    type = models.CharField(
        _('type'), max_length=ORDER_PRODUCT_ATTRIB_TYPE_MAX_LEN,
        choices=ProductType.get_feature_choices(),
        default=ProductType.MISCELLANEOUS.choice,
    )

    subscription = models.ForeignKey(Subscription, models.SET_NULL,
                                     blank=True, null=True)

    recipe = models.ForeignKey(Recipe, models.SET_NULL, blank=True, null=True)

    country = CountryField(blank=True, null=True)

    unit_price = models.DecimalField(
        _('unit price'), default=Decimal.from_float(0),
        decimal_places=PRICING_FACTOR, max_digits=PRICING_PLACES)

    base_currency = models.CharField(
        _('base currency'),
        max_length=ORDER_PRODUCT_ATTRIB_CURRENCY_CODE_MAX_LEN, blank=False,
        default=DEFAULT_CURRENCY.upper())

    description = models.CharField(
        _('description'), max_length=ORDER_PRODUCT_ATTRIB_DESC_MAX_LEN,
        default='')

    sku = models.CharField(
        _('order number'), max_length=ORDER_PRODUCT_ATTRIB_SKU_MAX_LEN,
        blank=False, unique=True
    )

    @dataclass
    class Meta:
        """ Model metadata """
        ordering = [f'{TYPE_FIELD}']

    @classmethod
    def numeric_fields(cls) -> list[str]:
        """ Get the list of numeric fields """
        return [
            OrderProduct.UNIT_PRICE_FIELD
        ]

    def __str__(self):
        desc = self.recipe if type in ProductType.recipe_options else \
            self.subscription if type in ProductType.subscription_options \
            else self.country if type in ProductType.delivery_options() else \
            self.description
        return f'{self.type} {desc}'


OrderProduct.SUBSCRIPTION_FIELDS.append(OrderProduct.id_field())
OrderProduct.INGREDIENT_BOX_FIELDS.append(OrderProduct.id_field())
OrderProduct.DELIVERY_FIELDS.append(OrderProduct.id_field())


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
    AMOUNT_BASE_FIELD = AMOUNT_BASE_FIELD
    ORDER_NUM_FIELD = ORDER_NUM_FIELD
    ITEMS_FIELD = ITEMS_FIELD
    WAS_1ST_X_FREE_FIELD = WAS_1ST_X_FREE_FIELD
    INFO_FIELD = INFO_FIELD
    ADDRESS_FIELD = ADDRESS_FIELD

    ORDER_ATTRIB_ORDER_NUM_MAX_LEN: int = 40
    ORDER_ATTRIB_INFO_MAX_LEN: int = 150
    ORDER_ATTRIB_STATUS_MAX_LEN: int = 2
    ORDER_ATTRIB_CURRENCY_CODE_MAX_LEN: int = CURRENCY_CODE_MAX_LEN

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    created = models.DateTimeField(_('created'), auto_now_add=True)
    updated = models.DateTimeField(_('updated'), auto_now=True)

    status = models.CharField(
        _('status'), max_length=ORDER_ATTRIB_STATUS_MAX_LEN,
        choices=OrderStatus.get_feature_choices(),
        default=OrderStatus.VOID.choice,
    )

    # amount/base_currency is what the customer paid
    amount = models.DecimalField(
        _('amount'), default=Decimal(0),
        decimal_places=PRICING_FACTOR, max_digits=PRICING_PLACES)
    base_currency = models.CharField(
        _('base currency'),
        max_length=ORDER_ATTRIB_CURRENCY_CODE_MAX_LEN, blank=False,
        default=DEFAULT_CURRENCY.upper())

    # amount_base is what the customer paid from the app's point of view
    amount_base = models.DecimalField(
        _('amount (app base currency)'), default=Decimal(0),
        decimal_places=PRICING_FACTOR, max_digits=PRICING_PLACES)

    order_num = models.CharField(
        _('order number'), max_length=ORDER_ATTRIB_ORDER_NUM_MAX_LEN,
        blank=False, unique=True
    )

    was_1st_x_free = models.BooleanField(
        default=False,
        help_text='Designates this order was a first x free delivery.')

    info = models.CharField(
        _('miscellaneous info'), max_length=ORDER_ATTRIB_INFO_MAX_LEN,
        blank=True
    )

    address = models.ForeignKey(Address, on_delete=models.CASCADE)

    items = models.ManyToManyField(OrderProduct, through='OrderItem')

    @dataclass
    class Meta:
        """ Model metadata """
        ordering = [f'{DATE_OLDEST_LOOKUP}{CREATED_FIELD}']

    @classmethod
    def date_fields(cls) -> list[str]:
        """ Get the list of date fields """
        return [
            Order.CREATED_FIELD, Order.UPDATED_FIELD
        ]

    @classmethod
    def numeric_fields(cls) -> list[str]:
        """ Get the list of numeric fields """
        return [
            Order.AMOUNT_FIELD, Order.AMOUNT_BASE_FIELD
        ]

    @classmethod
    def boolean_fields(cls) -> list[str]:
        """ Get the list of boolean fields """
        return [Order.WAS_1ST_X_FREE_FIELD]

    def __str__(self):
        return f'{self.order_num} {self.created} {str(self.user)}'


Order.SEARCH_DATE_FIELD = Order.UPDATED_FIELD


class OrderItem(ModelMixin, models.Model):
    """
    Order item model
    """
    ORDER_FIELD = ORDER_FIELD
    ORDER_PROD_FIELD = ORDER_PROD_FIELD
    QUANTITY_FIELD = QUANTITY_FIELD
    AMOUNT_FIELD = AMOUNT_FIELD
    BASE_CURRENCY_FIELD = BASE_CURRENCY_FIELD

    ORDER_ITEM_ATTRIB_CURRENCY_CODE_MAX_LEN: int = CURRENCY_CODE_MAX_LEN

    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    order_prod = models.ForeignKey(OrderProduct, on_delete=models.CASCADE)
    quantity = models.IntegerField(
        _('quantity of product'), blank=False, default=0)

    amount = models.DecimalField(
        _('subtotal amount'), default=Decimal(0),
        decimal_places=PRICING_FACTOR, max_digits=PRICING_PLACES)
    base_currency = models.CharField(
        _('currency'),
        max_length=ORDER_ITEM_ATTRIB_CURRENCY_CODE_MAX_LEN, blank=False,
        default=DEFAULT_CURRENCY.upper())

    @dataclass
    class Meta:
        """ Model metadata """

    def __str__(self):
        return f'{self.order} {self.order_prod} - {self.quantity}'
