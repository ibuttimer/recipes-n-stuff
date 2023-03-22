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
from random import uniform
from typing import List, Tuple

from django.contrib.auth.decorators import login_required
from django.core.exceptions import BadRequest
from django.http import HttpRequest
from django.shortcuts import redirect
from django.views.decorators.http import require_GET

from django_countries import countries

from order.constants import (
    INGREDIENT_QUERY, SUBSCRIPTION_QUERY, DELIVERY_QUERY
)
from recipes.models import Recipe
from recipesnstuff import HOME_ROUTE_NAME
from recipesnstuff.settings import PRICING_FACTOR, DEFAULT_CURRENCY
from subscription.models import Subscription
from utils.misc import is_boolean_true, Crud
from .utils import orderprod_permission_check
from ..misc import generate_sku, add_new_subscription_product
from ..models import ProductType, OrderProduct


INGREDIENT_MIN_PRICE = 3.0
INGREDIENT_MAX_PRICE = 6.0
STANDARD_DELIVER_MIN = 1.0
STANDARD_DELIVER_MAX = 1.99
PREMIUM_DELIVER_MIN = 2.0
PREMIUM_DELIVER_MAX = 2.99


@login_required
@require_GET
def generate_order_product(request: HttpRequest):
    """
    Generate order products
    :param request: current request
    :return: response
    """
    orderprod_permission_check(request, Crud.CREATE)

    to_generate = set()
    for query in [
        INGREDIENT_QUERY, SUBSCRIPTION_QUERY, DELIVERY_QUERY
    ]:
        if query in request.GET:
            if is_boolean_true(request.GET[query]):
                to_generate.add(query)
    if len(to_generate) == 0:
        raise BadRequest('Malformed request; query not specified')

    for query, generator in [
        (INGREDIENT_QUERY, generate_ingredient_order_prods),
        (SUBSCRIPTION_QUERY, generate_subscription_order_prods),
        (DELIVERY_QUERY, generate_delivery_order_prods),
    ]:
        if query in to_generate:
            generator()

    return redirect(HOME_ROUTE_NAME)


def generate_ingredient_order_prods():
    """
    Generate ingredient box order numbers
    """
    for recipe in list(Recipe.objects.values(
            Recipe.id_field(), Recipe.NAME_FIELD
    ).all()):
        sku = generate_sku(
            ProductType.INGREDIENT_BOX, recipe=recipe.get(Recipe.id_field()))
        if not OrderProduct.objects.filter(**{
            f'{OrderProduct.SKU_FIELD}': sku
        }).exists():
            OrderProduct.objects.create(**{
                f'{OrderProduct.TYPE_FIELD}':
                    ProductType.INGREDIENT_BOX.choice,
                f'{OrderProduct.SKU_FIELD}': sku,
                f'{OrderProduct.RECIPE_FIELD}': Recipe.get_by_id_field(
                    recipe.get(Recipe.id_field())),
                f'{OrderProduct.DESCRIPTION_FIELD}':
                    f'Ingredient box for {recipe.get(Recipe.NAME_FIELD)}',
                f'{OrderProduct.UNIT_PRICE_FIELD}':
                    generate_random_price(
                        INGREDIENT_MIN_PRICE, INGREDIENT_MAX_PRICE),
                f'{OrderProduct.BASE_CURRENCY_FIELD}': DEFAULT_CURRENCY.upper()
            })


def generate_subscription_order_prods():
    """
    Generate subscription order numbers
    """
    for sub in Subscription.objects.all():
        sku = generate_sku(ProductType.SUBSCRIPTION, subscription=sub)
        if not OrderProduct.objects.filter(**{
            f'{OrderProduct.SKU_FIELD}': sku
        }).exists():
            add_new_subscription_product(sub)


def delivery_options() -> List[Tuple]:
    """
    Generate delivery order product options for countries
    :return: list of options
    """
    del_opts = []
    for opt in ProductType.delivery_options():
        del_opts.extend([
            # (opt, sku, country, desc, pmin, pmax)
            (opt, generate_sku(opt, country=country), country.code,
             f'{opt.value.name} ({country.name})',
             STANDARD_DELIVER_MIN if opt == ProductType.STANDARD_DELIVERY else
             PREMIUM_DELIVER_MIN if opt == ProductType.PREMIUM_DELIVERY else 0,
             STANDARD_DELIVER_MAX if opt == ProductType.STANDARD_DELIVERY else
             PREMIUM_DELIVER_MAX if opt == ProductType.PREMIUM_DELIVERY else 0)
            for country in list(countries)
        ])
    return del_opts


def generate_delivery_order_prods():
    """
    Generate delivery order numbers
    """
    for opt, sku, country, desc, pmin, pmax in delivery_options():
        if not OrderProduct.objects.filter(**{
            f'{OrderProduct.SKU_FIELD}': sku
        }).exists():
            OrderProduct.objects.create(**{
                f'{OrderProduct.TYPE_FIELD}': opt.choice,
                f'{OrderProduct.SKU_FIELD}': sku,
                f'{OrderProduct.COUNTRY_FIELD}': country,
                f'{OrderProduct.DESCRIPTION_FIELD}': desc,
                f'{OrderProduct.UNIT_PRICE_FIELD}': generate_random_price(
                    pmin, pmax) if pmin > 0 else 0,
                f'{OrderProduct.BASE_CURRENCY_FIELD}': DEFAULT_CURRENCY.upper()
            })


def generate_random_price(min_price: float, max_price: float):
    """
    Generate a random price
    :param min_price: min price
    :param max_price: max price
    :return: price
    """
    return round(uniform(min_price, max_price), PRICING_FACTOR)
