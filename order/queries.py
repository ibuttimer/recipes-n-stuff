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
from typing import Union

from django.shortcuts import get_object_or_404

from order.models import OrderProduct, ProductType
from recipes.models import Recipe
from subscription.models import Subscription


def get_subscription_product(subscription: Subscription) -> OrderProduct:
    """
    Get the order product for `subscription`
    :param subscription: subscription to search for
    :return: OrderProduct
    """
    order_prod = OrderProduct.objects.get(**{
        f'{OrderProduct.TYPE_FIELD}': ProductType.SUBSCRIPTION.choice,
        f'{OrderProduct.SUBSCRIPTION_FIELD}': subscription
    })
    return order_prod


def get_ingredient_box_product(recipe: Union[Recipe, int]) -> OrderProduct:
    """
    Get the order product for `recipe`
    :param recipe: recipe to search for or its id
    :return: OrderProduct
    """
    if isinstance(recipe, int):
        recipe = get_object_or_404(Recipe, **{
            f'{Recipe.id_field()}': recipe
        })
    order_prod = OrderProduct.objects.get(**{
        f'{OrderProduct.TYPE_FIELD}': ProductType.INGREDIENT_BOX.choice,
        f'{OrderProduct.RECIPE_FIELD}': recipe
    })
    return order_prod
