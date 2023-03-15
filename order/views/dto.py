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
from typing import TypeVar
from decimal import Decimal

from base.dto import BaseDto
from checkout.basket import SUBSCRIPTION_IMAGE
from order.misc import order_prod_type_id
from order.views.order_queries import get_order
from order.models import Order, OrderProduct, OrderItem, ProductType
from profiles.dto import AddressDto
from recipes.constants import RECIPE_ID_ROUTE_NAME
from recipes.models import Recipe
from recipesnstuff import RECIPES_APP_NAME
from recipesnstuff.settings import DEFAULT_CURRENCY
from subscription.models import Subscription
from checkout.misc import format_amount_str
from utils import reverse_q, namespaced_url

TypeOrderDto = TypeVar("TypeOrderDto", bound="OrderDto")
TypeOrderProductDto = TypeVar("TypeOrderProductDto", bound="OrderProductDto")
TypeOrderIdsBundle = TypeVar("TypeOrderIdsBundle", bound="OrderIdsBundle")


IdQuantity = namedtuple(
    #               OrderProduct id, quantity, ProductType, type-specific id
    'IdQuantity', ['id', 'quantity', 'prod_type', 'type_id'],
    defaults=[None, None, None])


@dataclass
class OrderDto(BaseDto):
    """ Order data transfer object """

    @staticmethod
    def from_model(order: Order, *args,
                   all_attrib: bool = True) -> TypeOrderDto:
        """
        Generate a DTO from the specified `order`
        :param order: model instance to populate DTO from
        :param args: list of Order.xxx_FIELD names to populate in addition
                    to basic fields
        :param all_attrib: populate all attributes flag; default True
        :return: DTO instance
        """

        dto = BaseDto.from_model_to_obj(order, OrderDto())
        # custom handling for specific attributes

        dto.amount_str = format_amount_str(
            dto.amount, dto.base_currency, with_symbol=True)
        dto.item_cnt = order.items.count()

        if all_attrib or Order.ITEMS_FIELD in args:
            dto.items = list(
                map(lambda order_item: OrderProductDto.from_model(
                        order_item.order_prod,
                        **item_fields_for_prod_dto(order_item)
                    ), order.orderitem_set.all())
            )
        if all_attrib or Order.ADDRESS_FIELD in args:
            dto.address = AddressDto.from_model(order.address)

        return dto

    @staticmethod
    def from_id(pk: int, *args, all_attrib: bool = True) -> TypeOrderDto:
        """
        Generate a DTO from the specified order `id`
        :param pk: order id to populate DTO from
        :param args: list of Order.xxx_FIELD names to populate in addition
                    to basic fields
        :param all_attrib: populate all attributes flag; default True
        :return: DTO instance
        """
        order, _ = get_order(pk)
        return OrderDto.from_model(order, *args, all_attrib=all_attrib)


def item_fields_for_prod_dto(order_item: OrderItem) -> dict:
    """
    Get the field data to create a OrderProductDto from an OrderItem
    :param order_item: order item
    :return: dict of info
    """
    values = {
        k: getattr(order_item, k) for k in [
            OrderItem.QUANTITY_FIELD, OrderItem.AMOUNT_FIELD,
            OrderItem.BASE_CURRENCY_FIELD
        ]
    }
    return values


@dataclass
class OrderProductDto(BaseDto):
    """ OrderProduct data transfer object """

    @staticmethod
    def from_model(order_prod: OrderProduct, *args, all_attrib: bool = True,
                   quantity: int = 0, amount: Decimal = 0,
                   base_currency: str = DEFAULT_CURRENCY
                   ) -> TypeOrderProductDto:
        """
        Generate a DTO from the specified `order_prod`
        :param order_prod: model instance to populate DTO from
        :param args: list of OrderProduct.xxx_FIELD names to populate in
                    addition to basic fields
        :param all_attrib: populate all attributes flag; default True
        :param quantity: quantity of order_prod; default 0
        :param amount: subtotal amount for order_prod; default 0
        :param base_currency: currency for amount
        :return: DTO instance
        """
        dto = BaseDto.from_model_to_obj(order_prod, OrderProductDto())
        # custom handling for specific attributes
        if all_attrib or OrderProduct.SUBSCRIPTION_FIELD in args:
            dto.subscription = Subscription.get_by_id_field(
                dto.subscription_id) if dto.subscription_id else None
        if all_attrib or OrderProduct.RECIPE_FIELD in args:
            dto.recipe = Recipe.get_by_id_field(dto.recipe_id) \
                if dto.recipe_id else None

        dto.image = dto.recipe.main_image if dto.recipe else \
            SUBSCRIPTION_IMAGE if dto.subscription else None

        dto.quantity = quantity
        dto.subtotal = format_amount_str(
            amount, base_currency, with_symbol=True)
        dto.url = reverse_q(
            namespaced_url(RECIPES_APP_NAME, RECIPE_ID_ROUTE_NAME),
            args=[order_prod.recipe.id]
        )

        return dto

    @staticmethod
    def from_id(pk: int, *args, all_attrib: bool = True, quantity: int = 0,
                amount: Decimal = 0,
                base_currency: str = DEFAULT_CURRENCY) -> TypeOrderProductDto:
        """
        Generate a DTO from the specified order_prod `id`
        :param pk: order_prod id to populate DTO from
        :param args: list of Order.xxx_FIELD names to populate in addition
                    to basic fields
        :param all_attrib: populate all attributes flag; default True
        :param quantity: quantity of order_prod; default 0
        :param amount: subtotal amount for order_prod; default 0
        :param base_currency: currency for amount
        :return: DTO instance
        """
        order_prod = OrderProduct.get_by_id_field(pk)
        return OrderProductDto.from_model(
            order_prod, *args, all_attrib=all_attrib, quantity=quantity,
            amount=amount, base_currency=base_currency)


@dataclass
class OrderIdsBundle(BaseDto):
    """ Order Ids bundle data transfer object """

    @staticmethod
    def from_model(order: Order) -> TypeOrderIdsBundle:
        """
        Generate a DTO from the specified `order`
        :param order: model instance to populate DTO from
        :return: DTO instance
        """
        dto = BaseDto.from_model_to_obj(
            order, OrderIdsBundle(),
            exclude=BaseDto.model_fields_difference(Order, Order.id_field()))
        # custom handling for specific attributes
        dto.items = list(
            map(lambda order_item:
                IdQuantity(
                    id=order_item.order_prod.id, quantity=order_item.quantity,
                    prod_type=ProductType.from_choice(
                        order_item.order_prod.type),
                    type_id=order_prod_type_id(order_item)
                ), order.orderitem_set.all())
        )
        return dto

    @staticmethod
    def from_id(pk: int) -> TypeOrderIdsBundle:
        """
        Generate a DTO from the specified order `id`
        :param pk: order id to populate DTO from
        :return: DTO instance
        """
        order, _ = get_order(pk)
        return OrderIdsBundle.from_model(order)
