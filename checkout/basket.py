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
from typing import List, Union, TypeVar, Tuple, Optional
from dataclasses import dataclass
from decimal import Decimal

from django.http import HttpRequest
import json_fix
import jsonpickle
from django.template.loader import render_to_string

from base.dto import ImagePool
from base.views import info_toast_payload, InfoModalTemplate
from order.misc import generate_order_num
from order.models import OrderProduct
from order.queries import get_subscription_product, get_ingredient_box_product
from recipes.constants import RECIPE_ID_ROUTE_NAME
from recipes.models import Recipe
from recipesnstuff import BASE_APP_NAME, RECIPES_APP_NAME
from recipesnstuff.settings import FINANCIAL_FACTOR, DEFAULT_CURRENCY
from subscription.models import Subscription
from user.models import User
from utils import (
    replace_inner_html_payload, app_template_path, reverse_q, namespaced_url
)

from .constants import (
    THIS_APP, BASKET_SES, BASKET_ITEM_COUNT_CTX, BASKET_TOTAL_CTX,
    ADDED_CTX, UPDATED_CTX, COUNT_CTX
)
from .currency import is_valid_code, get_currency
from .forex import NumType, convert_forex, normalise_amount

# workaround for self type hints from https://peps.python.org/pep-0673/
TypeBasketItem = TypeVar("TypeBasketItem", bound="BasketItem")
TypeBasket = TypeVar("TypeBasket", bound="Basket")


SUBSCRIPTION_IMAGE = ImagePool.of_static('img/visa-1623894_640.jpg')

MAX_DISPLAY_COUNT = 99

BasketUpdate = namedtuple('BasketUpdate', ['added', 'updated', 'count'],
                          defaults=[False, False, 0])


@dataclass
class BasketItem:
    """ Class representing an entry in the payment basket """
    currency: str
    amount: Union[int, float, Decimal]
    count: int
    description: str
    sku: str
    instructions: str
    url: str
    image: ImagePool

    def cost(self, as_decimal: bool = False) -> Union[int, float, Decimal]:
        """
        Total cost in item base currency
        :param as_decimal: as Decimal flag; default False
        :return: total cost
        """
        cost = self.amount * self.count \
            if not isinstance(self.amount, Decimal) else \
            self.amount * Decimal.from_float(self.count)
        return cost if not as_decimal else cost \
            if isinstance(cost, Decimal) else Decimal.from_float(cost)

    @property
    def item_total(self):
        return self.cost(as_decimal=False)

    @staticmethod
    def format_amount_str(amt: float, code: str, with_symbol: bool = False):
        """
        Get a formatted amount string
        :param amt: amount
        :param code: currency code
        :param with_symbol: include currency symbol flag; default False
        :return: formatted string
        """
        currency = get_currency(code)
        symbol = f'{currency.symbol} ' if with_symbol else ''
        return f'{symbol}{amt:.{currency.digits}f}'

    def _format_amt_str(self, amt: float):
        return self.format_amount_str(amt, self.currency)

    @property
    def amt_str(self):
        return self._format_amt_str(self.amount)

    @property
    def item_total_str(self):
        return self._format_amt_str(self.item_total)

    def receipt_dict(self) -> dict:
        """
        Get the item entry for a receipt
        :return: item entry
        """
        return {
            'sku': self.sku,
            'description': self.description,
            'price': self.amount,
            'currency': self.currency,
            'units': self.count,
            'instructions': self.instructions,
        }

    TYPE_MARKER = 'type'
    ATTRIB_SKU = 'sku'
    ATTRIB_DESCRIPTION = 'description'
    ATTRIB_AMOUNT = 'amount'
    ATTRIB_CURRENCY = 'currency'
    ATTRIB_UNITS = 'units'
    ATTRIB_INSTRUCTIONS = 'instructions'
    ATTRIB_URL = 'url'
    ATTRIB_IMAGE = 'image'

    def __json__(self):
        """ Return a built-in object that is naturally jsonable """
        return jsonpickle.encode(self)

    @staticmethod
    def from_jsonable(jsonable: dict) -> TypeBasketItem:
        """
        Convert json representation to BasketItem
        :param jsonable: json representation
        :return: BasketItem if found otherwise original argument
        """
        return jsonpickle.decode(jsonable)


class Basket:
    """ Class representing a payment basket """
    _currency: str = ''
    _currency_symbol: str = ''
    items: List[BasketItem] = []
    subtotals: List[float]
    _total: Decimal
    order_num: str = ''
    user: User

    def __init__(self, currency: str = None, request: HttpRequest = None):
        self._initialise(currency)
        self._new_order(request)

    def _initialise(self, currency: str):
        """
        Initialise the basket
        :param currency: basket currency code
        """
        self.currency = (currency or DEFAULT_CURRENCY).upper()
        self.items = []
        self.subtotals = []
        self._total = Decimal.from_float(0)

    def _new_order(self, request: HttpRequest):
        """
        Start a new order
        :param request: http request
        """
        if not self.order_num:
            if request and request.user.is_authenticated:
                self.order_num = generate_order_num(request)
                self.user = request.user
            else:
                self.order_num = ''
                self.user = None

    def add(self, request: HttpRequest, amount: Union[int, float, Decimal],
            description: str, count: int = 1, sku: str = None,
            currency: str = None, instructions: str = None, url: str = None,
            image: ImagePool = None) -> BasketUpdate:
        """
        Add an item to the basket
        :param request: http request
        :param amount: cost per item
        :param description: description
        :param count: number of items
        :param sku: stock keeping unit; default None
        :param currency: currency code; default None i.e. basket currency
        :param instructions: additional instructions; default None
        :param url: product url; default None
        :param image: image url: default None
        :return BasketUpdate
        """
        self._new_order(request)
        currency = currency or self._currency

        basket_item = self.get_item(sku)
        if basket_item is None:
            # add new item
            basket_item = BasketItem(
                currency=currency, amount=amount, count=count,
                description=description, sku=sku, instructions=instructions,
                url=url, image=image
            )
            self.items.append(basket_item)
            self.subtotals.append(0)
            added = True
        else:
            # update existing item
            assert basket_item.currency == currency
            assert basket_item.amount == amount
            basket_item.count += count
            added = False

        self._calc_total()

        return BasketUpdate(
            added=added, updated=not added, count=basket_item.count)

    def add_order_product(self, request: HttpRequest, order_prod: OrderProduct,
                          count: int = 1, instructions: str = None,
                          url: str = None,
                          image: ImagePool = None) -> BasketUpdate:
        """
        Add an item to the basket
        :param request: http request
        :param order_prod: product to add
        :param count: number of items
        :param instructions: additional instructions; default None
        :param url: product url; default None
        :param image: image url: default None
        """
        return self.add(
            request, order_prod.unit_price, order_prod.description,
            count=count, sku=order_prod.sku,
            currency=order_prod.base_currency, instructions=instructions,
            url=url, image=image
        )

    def contains_item(self, sku: str):
        """
        Check if an item is in the basket
        :param sku: stock keeping unit
        """
        return sum(map(lambda item: item.sku == sku, self.items)) > 0

    def get_item(self, sku: str) -> Optional[BasketItem]:
        """
        Check if an item is in the basket
        :param sku: stock keeping unit
        """
        items = list(filter(lambda item: item.sku == sku, self.items))
        assert len(items) <= 1
        return items[0] if len(items) > 0 else None

    def remove(self, index: int) -> bool:
        """
        Remove an item from the basket
        :param index: index of item
        :return: True if basket updated
        """
        success = False
        if 0 <= index < self.num_items:
            del self.items[index]
            del self.subtotals[index]
            self._calc_total()
            success = True
        return success

    def clear(self, request: HttpRequest = None):
        """
        Clear the basket
        """
        self._initialise(self._currency)
        self.add_to_request(request)

    def close(self, request: HttpRequest = None):
        """
        Close the basket
        """
        self._initialise(DEFAULT_CURRENCY)
        self.order_num = ''
        self.user = None
        self.add_to_request(request)

    def add_to_request(self, request: HttpRequest):
        """
        Add this basket to the request session.
        :param request: http request
        """
        if request:
            request.session[BASKET_SES] = self

    def _calc_total(self):
        """ Calculate the current basket total """
        total = Decimal.from_float(0)
        for index, item in enumerate(self.items):
            cost = item.cost(as_decimal=True)
            if item.currency != self._currency:
                cost = convert_forex(cost, item.currency, self._currency,
                                     factor=FINANCIAL_FACTOR,
                                     result_as=NumType.DECIMAL)
            self.subtotals[index] = \
                BasketItem.format_amount_str(cost, self._currency)
            total += cost

        self._total = total

    @property
    def num_items(self) -> int:
        """
        Get number of items in the basket
        :return: number of items
        """
        return sum(
            map(lambda item: item.count, self.items)
        )

    @property
    def currency(self):
        """ Get the currency code of the basket """
        return self._currency

    @property
    def currency_symbol(self):
        """ Get the currency symbol of the basket """
        return self._currency_symbol

    @currency.setter
    def currency(self, code: str):
        """
        Set the currency code of the basket
        :param code: code of currency to set
        """
        if is_valid_code(code):
            currency = get_currency(code)
            self._currency = currency.code
            self._currency_symbol = currency.symbol
            self._calc_total()
        else:
            raise ValueError(f'Unsupported currency: {code}')

    def update_item_units(self, index: int, units: int):
        """
        Update an item's unit count
        :param index: zero-based index of item
        :param units: number of units
        :return: True if basket updated
        """
        success = False
        if 0 <= index < self.num_items and units > 0:
            self.items[index].count = units
            self._calc_total()
            success = True

        return success

    @property
    def total(self) -> float:
        """
        Get the current basket total in basket currency for display purposes
        :return: total
        """
        return normalise_amount(self._total, self._currency)

    @property
    def total_str(self):
        return BasketItem.format_amount_str(self.total, self._currency)

    def format_total_str(self, with_symbol: bool = False):
        """
        Get a formatted basket total amount string
        :param with_symbol: include currency symbol flag; default False
        :return: formatted string
        """
        return BasketItem.format_amount_str(
            self.total, self._currency, with_symbol=with_symbol)

    @property
    def payment_total(self) -> int:
        """
        Get the current basket total in basket currency for payment purposes
        i.e. amount to send to payment provider
        :return: total
        """
        return normalise_amount(
            self._total, self._currency, smallest_unit=True)

    def receipt_dict(self) -> dict:
        """
        Get the item entry for a receipt
        :return: item entry
        """
        return {
            'items': [
                item.receipt_dict() for item in self.items
            ],
            'total': self.total,
            'currency': self.currency,
        }

    def __json__(self):
        """ Return a built-in object that is naturally jsonable """
        return jsonpickle.encode(self)

    @staticmethod
    def from_jsonable(jsonable: dict) -> TypeBasket:
        """
        Convert json representation to Basket
        :param jsonable: json representation
        :return: Basket if found otherwise original argument
        """
        return jsonpickle.decode(jsonable)


def get_session_basket(request: HttpRequest) -> Tuple[Basket, bool]:
    """
    Get the session basket
    :param request: http request
    :return tuple of basket and new basket flag
    """
    new_order = BASKET_SES not in request.session
    basket = Basket(request=request) if new_order else \
        Basket.from_jsonable(request.session[BASKET_SES])
    request.session[BASKET_SES] = basket
    return basket, new_order


def add_subscription_to_basket(
        request: HttpRequest, subscription: Subscription, count: int = 1,
        instructions: str = None):
    """
    Add an item to the request basket
    :param request: http request
    :param subscription: subscription
    :param count: number of items; default 1
    :param instructions: additional instructions; default None
    :return navbar basket html payload
    """
    basket, _ = get_session_basket(request)

    order_prod = get_subscription_product(subscription)

    basket.add_order_product(
        request, order_prod, count=count, instructions=instructions,
        image=SUBSCRIPTION_IMAGE)

    return navbar_basket_html(basket)


def add_ingredient_box_to_basket(
        request: HttpRequest, recipe: Union[Recipe, int], count: int = 1,
        instructions: str = None) -> dict:
    """
    Add an item to the request basket
    :param request: http request
    :param recipe: recipe, or it's id
    :param count: number of items; default 1
    :param instructions: additional instructions; default None
    :return navbar basket html payload
    """
    basket, _ = get_session_basket(request)

    order_prod = get_ingredient_box_product(recipe)

    result = basket.add_order_product(
        request, order_prod, count=count, instructions=instructions,
        url=reverse_q(
            namespaced_url(RECIPES_APP_NAME, RECIPE_ID_ROUTE_NAME),
            args=[recipe.id]
        ),
        image=recipe.main_image
    )

    return navbar_basket_html(basket, result)


def navbar_basket_html(basket: Basket, result: BasketUpdate = None):
    """
    Get the html code for the navbar basket
    :param basket: basket
    :param result: basket update result; default None
    :return: payload
    """
    payload = replace_inner_html_payload(
        "#id__navbar-basket-container",
        render_to_string(
            app_template_path(
                BASE_APP_NAME, "snippet", "navbar_basket.html"),
            context=navbar_basket_context(basket)
        ),
        tooltips_selector='#id__navbar-basket-tooltip'
    )
    if result:
        payload.update(
            info_toast_payload(InfoModalTemplate(app_template_path(
                THIS_APP, "messages", "basket_updated.html"),
                context={
                    ADDED_CTX: result.added,
                    UPDATED_CTX: result.updated,
                    COUNT_CTX: result.count
                }))
        )
    return payload


def navbar_basket_context(basket: Basket) -> dict:
    """
    Get the context for the navbar basket rendering
    :param basket: basket
    :return: context
    """
    return {
        BASKET_ITEM_COUNT_CTX: basket.num_items
        if basket.num_items <= MAX_DISPLAY_COUNT else f'{MAX_DISPLAY_COUNT}+',
        BASKET_TOTAL_CTX: basket.format_total_str(with_symbol=True)
    }
