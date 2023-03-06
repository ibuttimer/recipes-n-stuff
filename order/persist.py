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
from _decimal import Decimal

from checkout.basket import Basket
from checkout.forex import convert_forex, NumType
from order.models import Order, OrderStatus, OrderProduct
from recipesnstuff.settings import DEFAULT_CURRENCY
from subscription.models import FeatureType


def save_order(basket: Basket):
    """
    Save the basket order to the database
    :param basket: basket to save
    """
    total = Decimal.from_float(basket.total)
    order = Order.objects.create(**{
        f'{Order.ORDER_NUM_FIELD}': basket.order_num,
        f'{Order.USER_FIELD}': basket.user,
        f'{Order.STATUS_FIELD}': OrderStatus.PAID.choice,
        f'{Order.AMOUNT_FIELD}': total,
        f'{Order.BASE_CURRENCY_FIELD}': basket.currency,
        f'{Order.AMOUNT_BASE_FIELD}': convert_forex(
            total, basket.currency, DEFAULT_CURRENCY.upper(),
            result_as=NumType.DECIMAL),
        f'{Order.WAS_1ST_X_FREE_FIELD}':
            basket.feature_type == FeatureType.FIRST_X_FREE
    })

    order.items.set(
        OrderProduct.objects.get(**{
            f'{OrderProduct.SKU_FIELD}': item.sku
        }) for item in basket.items
    )
    order.save()
