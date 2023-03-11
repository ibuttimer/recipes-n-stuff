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
from typing import TypeVar

from base.dto import BaseDto
from checkout.basket import SUBSCRIPTION_IMAGE
from order.views.order_queries import (
    # get_order_products_list,
    get_order
)
from order.models import Order, OrderProduct
from recipes.models import Recipe
from subscription.models import Subscription
from checkout.misc import format_amount_str

TypeOrderDto = TypeVar("TypeOrderDto", bound="OrderDto")


@dataclass
class OrderDto(BaseDto):
    """ Order data transfer object """

    @staticmethod
    def from_model(order: Order, *args, all_attrib: bool = True):
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
                        order_item.order_prod, quantity=order_item.quantity
                    ), order.orderitem_set.all())
            )

        return dto

    @staticmethod
    def from_id(pk: int, *args, all_attrib: bool = True):
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


@dataclass
class OrderProductDto(BaseDto):
    """ OrderProduct data transfer object """

    @staticmethod
    def from_model(order_prod: OrderProduct, *args, all_attrib: bool = True,
                   quantity: int = 0):
        """
        Generate a DTO from the specified `order_prod`
        :param order_prod: model instance to populate DTO from
        :param args: list of OrderProduct.xxx_FIELD names to populate in
                    addition to basic fields
        :param all_attrib: populate all attributes flag; default True
        :param quantity: quantity of order_prod; default 0
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

        return dto

    @staticmethod
    def from_id(pk: int, *args, all_attrib: bool = True, quantity: int = 0):
        """
        Generate a DTO from the specified order_prod `id`
        :param pk: order_prod id to populate DTO from
        :param args: list of Order.xxx_FIELD names to populate in addition
                    to basic fields
        :param all_attrib: populate all attributes flag; default True
        :param quantity: quantity of order_prod; default 0
        :return: DTO instance
        """
        order_prod = OrderProduct.get_by_id_field(pk)
        return OrderDto.from_model(order_prod, *args, all_attrib=all_attrib,
                                   quantity=quantity)
