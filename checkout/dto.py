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
from checkout.basket import Basket
from checkout.misc import calc_ccy_cost, format_amount_str
from order.models import OrderProduct


@dataclass
class DeliveryDto(BaseDto):

    @staticmethod
    def from_model(order_product: OrderProduct, basket: Basket,
                   is_selected: bool = False, detail: str = None,
                   feature_type: str = None):
        """
        Generate a DTO from the specified `model`
        :param order_product: model instance to populate DTO from
        :param basket: current basket
        :param is_selected: is selected flag; default False
        :param detail: detail message to display: default cost per item
        :param feature_type: choice for subscription FeatureType for free
                            delivery; default None
        :return: DTO instance
        """
        dto = BaseDto.from_model_to_obj(
            order_product, DeliveryDto(),
            exclude=BaseDto.model_fields_difference(
                order_product, OrderProduct.DELIVERY_FIELDS))
        # custom handling for specific attributes
        cost = calc_ccy_cost(
            order_product.unit_price, order_product.base_currency,
            basket.currency)
        cost = format_amount_str(cost, basket.currency, with_symbol=True)
        dto.detail = detail or f'{cost} per item'

        charge = basket.format_delivery_charge_str(
            with_symbol=True, delivery_opt=order_product)
        dto.description = f'{dto.description} - {charge}'

        dto.is_selected = is_selected
        dto.feature_type = feature_type

        return dto
