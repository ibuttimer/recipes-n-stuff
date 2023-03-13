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
from typing import List, Union

from _decimal import Decimal

from checkout.basket import Basket, BasketItem
from checkout.forex import convert_forex, NumType
from order.models import Order, OrderStatus, OrderProduct, OrderItem
from recipesnstuff.settings import DEFAULT_CURRENCY
from subscription.models import FeatureType


def save_order(basket: Basket, status: OrderStatus = OrderStatus.IN_PROGRESS):
    """
    Save the basket order to the database or update if already exists
    :param basket: basket to save
    :param status: order status; default OrderStatus.IN_PROGRESS
    """
    total = Decimal.from_float(basket.total)

    query_param = {
        f'{Order.ORDER_NUM_FIELD}': basket.order_num
    }
    order_info = {
        f'{Order.USER_FIELD}': basket.user,
        f'{Order.STATUS_FIELD}': status.choice,
        f'{Order.AMOUNT_FIELD}': total,
        f'{Order.BASE_CURRENCY_FIELD}': basket.currency,
        f'{Order.AMOUNT_BASE_FIELD}': convert_forex(
            total, basket.currency, DEFAULT_CURRENCY.upper(),
            result_as=NumType.DECIMAL),
        f'{Order.WAS_1ST_X_FREE_FIELD}':
            basket.feature_type == FeatureType.FIRST_X_FREE,
        f'{Order.ADDRESS_FIELD}': basket.address
    }

    if Order.objects.filter(**query_param).exists():
        # update existing order
        update_order(basket.order_num, order_info, items=basket.items)
    else:
        # save new order
        query_param.update(order_info)
        order = Order.objects.create(**query_param)
        order_set_items(order, basket.items)
        order.save()


def update_order(order_num: str, updates: dict,
                 items: List[Union[BasketItem, str]] = None):
    """
    Update an order's status
    :param order_num: order number
    :param updates: updates to apply
    :param items: list of items; default None, i.e. no change
    """
    order = Order.filter_by_field(Order.ORDER_NUM_FIELD, order_num)
    order.update(**updates)
    order = order.first()
    order_set_items(order, items)
    order.save()


def order_set_items(order: Order,
                    items: List[Union[BasketItem, str]]):
    """
    Update an order's items
    :param order: order
    :param items: list of items; None means no change
    """
    if items is not None:
        order.items.clear()     # clear previous basket items

        for item in items:
            OrderItem.objects.create(**{
                f'{OrderItem.ORDER_PROD_FIELD}': OrderProduct.get_by_field(
                    OrderProduct.SKU_FIELD,
                    item.sku if isinstance(item, BasketItem) else item
                ),
                f'{OrderItem.QUANTITY_FIELD}': item.count,
                f'{OrderItem.AMOUNT_FIELD}': item.cost(as_decimal=True),
                f'{OrderItem.BASE_CURRENCY_FIELD}': item.currency,
                f'{OrderItem.ORDER_FIELD}': order
            })

        order.save()


def update_order_status(order_num: str, status: OrderStatus, info: str = None):
    """
    Update an order's status
    :param order_num: order number
    :param status: new status
    :param info: additional into to save; default None
    """
    update = {
        f'{Order.STATUS_FIELD}': status.choice
    }
    if info:
        update[Order.INFO_FIELD] = info
    update_order(order_num, update)
