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
from typing import Union, Tuple

from django.db.models import QuerySet
from django.shortcuts import get_object_or_404

from order.models import OrderProduct, ProductType, Order, OrderStatus
from recipes.models import Recipe
from subscription.models import Subscription
from subscription.subscription_queries import user_has_subscription
from user.models import User


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


def get_delivery_product(
        country: str, del_type: ProductType = None) -> QuerySet:
    """
    Get the delivery products for `country`
    :param country: ISO 3166-1 alpha-2 code for country
    :param del_type: delivery type; default all
    :return: list of OrderProduct
    """
    query_param = {
        f'{OrderProduct.TYPE_FIELD}__in': [
            prod_type.choice for prod_type in ProductType.delivery_options()
        ]
    } if del_type is None else {
        f'{OrderProduct.TYPE_FIELD}': del_type.choice
    }
    query_param[OrderProduct.COUNTRY_FIELD] = country

    return OrderProduct.objects.filter(**query_param)\
        .order_by(OrderProduct.TYPE_FIELD)


def get_user_spending(user: User) -> Tuple[float, int, int]:
    """
    Get the spending for `user` since the start of their current subscription
    :param user: user to check
    :return: tuple of total amount in app base currency, number of orders, and
            number of first x free delivery orders
    """
    _, user_sub, _ = user_has_subscription(user)

    queryset = Order.objects.filter(**{
        f'{Order.USER_FIELD}': user,
        f'{Order.STATUS_FIELD}': OrderStatus.PAID.choice,
        f'{Order.UPDATED_FIELD}__gte': user_sub.start_date,
    }).exclude(**{
        # exclude subscriptions
        f'{Order.ITEMS_FIELD}__{OrderProduct.TYPE_FIELD}':
            ProductType.SUBSCRIPTION.choice,
    })

    return sum(list(map(
        lambda order: order.amount_base, queryset.all()
    ))), queryset.count(), len(list(map(
        lambda order: order.amount_base, queryset.filter(**{
            f'{Order.WAS_1ST_X_FREE_FIELD}': True
        }).all()
    )))
