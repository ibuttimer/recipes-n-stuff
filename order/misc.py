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
from collections import namedtuple
from enum import IntEnum, auto
from typing import Any

from django.http import HttpRequest
from django.shortcuts import get_object_or_404

from django_countries import countries
from more_itertools import nth

from checkout.currency import get_currency
from recipes.models import Recipe
from recipesnstuff.settings import DEFAULT_CURRENCY
from subscription.models import Subscription

from .models import ProductType, OrderProduct, OrderItem

SKU_DECODE_FIELDS = ['prod_type', 'subscription', 'recipe', 'country', 'ccy']


class SkuFields(IntEnum):
    """
    Enum representing SKU_DECODE_FIELDS indices
    Based on https://stackoverflow.com/a/61438054/4054609
    """
    def _generate_next_value_(name, start, count, last_values):
        """ generate consecutive automatic numbers starting from zero """
        return count

    PROD_TYPE = auto()
    SUBSCRIPTION = auto()
    RECIPE = auto()
    COUNTRY = auto()
    CCY = auto()


SkuDecode = namedtuple(
    'SkuDecode', SKU_DECODE_FIELDS, defaults=[None for _ in SKU_DECODE_FIELDS]
)

SKU_ID_DIGITS = 8
SKU_CCY_DIGITS = 3


def generate_sku(
        prod_type: ProductType, subscription: Subscription = None,
        recipe: Recipe = None, country: dict = None) -> str:
    """
    Generate an order product sku.
    ** Note: sku should be app-wide unique **
    :param prod_type: product type
    :param subscription: subscription instance; default None
    :param recipe: recipe instance; default None
    :param country: ISO 3166-1 alpha-2 code for country
    :return: sku
    """
    if prod_type in ProductType.subscription_options():
        identifier = subscription.id
        code = subscription.base_currency
    elif prod_type in ProductType.recipe_options():
        identifier = recipe.id
        code = DEFAULT_CURRENCY
    elif prod_type in ProductType.delivery_options():
        identifier = countries.alt_codes[country.code][1]
        code = DEFAULT_CURRENCY
    else:
        raise NotImplementedError(f'Not currently supported: {prod_type}')

    currency = get_currency(code)

    return f'{prod_type.choice.upper()}{identifier:0{SKU_ID_DIGITS}d}' \
           f'{currency.numeric_code:0{SKU_CCY_DIGITS}d}'


def order_prod_type_id(order_item: OrderItem) -> Any:
    """
    Get the order product type-specific id of the entity.
    :param order_item: order product
    :return: type id
    """
    order_prod = order_item.order_prod
    prod_type = ProductType.from_choice(order_prod.type)
    if prod_type in ProductType.subscription_options():
        identifier = order_prod.subscription.id
    elif prod_type in ProductType.recipe_options():
        identifier = order_prod.recipe.id
    elif prod_type in ProductType.delivery_options():
        identifier = countries.alt_codes[order_prod.country.code][1]
    else:
        raise NotImplementedError(f'Not currently supported: {prod_type}')

    return identifier


def decode_sku(sku: str) -> SkuDecode:
    """
    Decode an order product sku.
    :param sku:
    :return: decoded sku
    """
    assert len(sku) >= SKU_ID_DIGITS + SKU_CCY_DIGITS + 1

    ccy = get_currency(int(sku[-SKU_CCY_DIGITS:]))
    identifier = int(sku[-(SKU_ID_DIGITS + SKU_CCY_DIGITS):-SKU_CCY_DIGITS])
    prod_type: ProductType = ProductType.from_choice(
        sku[:-(SKU_ID_DIGITS + SKU_CCY_DIGITS)])

    info = {
        fld: None for fld in SKU_DECODE_FIELDS
    }
    info[SKU_DECODE_FIELDS[SkuFields.PROD_TYPE]] = prod_type
    info[SKU_DECODE_FIELDS[SkuFields.CCY]] = ccy

    if prod_type.is_subscription_option:
        info[SKU_DECODE_FIELDS[SkuFields.SUBSCRIPTION]] = get_object_or_404(
            Subscription, **Subscription.id_field_query(identifier))
    elif prod_type.is_recipe_option:
        info[SKU_DECODE_FIELDS[SkuFields.RECIPE]] = get_object_or_404(
            Recipe, **Recipe.id_field_query(identifier))
    elif prod_type.is_delivery_option:
        info[SKU_DECODE_FIELDS[SkuFields.COUNTRY]] = nth(
            filter(lambda key, val: val[1] == identifier,
                   countries.alt_codes.items()),
            0)

    return SkuDecode(**info)


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
