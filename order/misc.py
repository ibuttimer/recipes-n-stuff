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
import time

from django.http import HttpRequest

from checkout.currency import get_currency
from recipes.models import Recipe
from recipesnstuff.settings import DEFAULT_CURRENCY
from subscription.models import Subscription

from .models import ProductType, OrderProduct


def generate_sku(
        prod_type: ProductType, subscription: Subscription = None,
        recipe: Recipe = None) -> str:
    """
    Generate an order product sku.
    ** Note: sku should be app-wide unique **
    :param prod_type: product type
    :param subscription: subscription instance; default None
    :param recipe: recipe instance; default None
    :return: sku
    """
    if prod_type == ProductType.SUBSCRIPTION:
        identifier = subscription.id
        code = subscription.base_currency
    elif prod_type == ProductType.INGREDIENT_BOX:
        identifier = recipe.id
        code = DEFAULT_CURRENCY
    else:
        raise NotImplementedError(f'Not currently supported: {prod_type}')

    currency = get_currency(code)

    return f'{prod_type.choice.upper()}{identifier:08d}' \
           f'{currency.numeric_code:03d}'


def generate_order_num(request: HttpRequest):
    """
    Generate an order number
    :param request: http request
    :return:
    """
    # strip leading '0x' to give 7 digit user id
    user_id = f'{request.user.id:0<#9X}'[2:]
    # strip leading '0x' to give 11 digit timestamp
    timestamp = int(time.time_ns() / 10**6)   # timestamp in msec
    timestamp = f'{timestamp:0<#13X}'[2:]
    return f'{user_id}{timestamp}'


def add_new_subscription_product(subscription: Subscription):
    """
    Add a new subscription product
    :param subscription: subscription
    :return:
    """
    prod_type = ProductType.SUBSCRIPTION
    OrderProduct.objects.create(**{
        f'{OrderProduct.TYPE_FIELD}': prod_type.choice,
        f'{OrderProduct.SKU_FIELD}':
            generate_sku(prod_type, subscription=subscription),
        f'{OrderProduct.SUBSCRIPTION_FIELD}': subscription
    })
