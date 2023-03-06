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
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string

from base.dto import ImagePool
from base.views import info_toast_payload, InfoModalTemplate
from order.misc import generate_order_num
from order.models import OrderProduct, ProductType
from order.queries import (
    get_subscription_product, get_ingredient_box_product, get_delivery_product
)
from profiles.enums import AddressType
from profiles.models import Address
from profiles.views import addresses_query
from recipes.constants import RECIPE_ID_ROUTE_NAME
from recipes.models import Recipe
from recipesnstuff import BASE_APP_NAME, RECIPES_APP_NAME
from recipesnstuff.settings import (
    FINANCIAL_FACTOR, DEFAULT_CURRENCY, PRICING_FACTOR
)
from subscription.models import Subscription, FeatureType
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
from .misc import calc_cost, format_amount_str, calc_ccy_cost

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
        return calc_cost(self.amount, self.count, as_decimal=as_decimal)

    @property
    def item_total(self):
        return self.cost(as_decimal=False)

    def _format_amt_str(self, amt: float):
        return format_amount_str(amt, self.currency)

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
    subtotals: List[float]          # item subtotals ex delivery
    _subtotal: Decimal              # subtotal ex delivery
    _delivery_charge: Decimal       # delivery change
    _total: Decimal                 # total inc delivery
    order_num: str = ''
    closed: bool = True
    user: User
    address: Address = None
    _delivery: OrderProduct = None
    # subscription feature type for a free delivery
    _feature_type: FeatureType = None

    def __init__(self, currency: str = None, request: HttpRequest = None):
        self._initialise(currency)
        self._new_order(request)

    def _initialise(self, currency: str):
        """
        Initialise the basket
        :param currency: currency code for basket
        """
        self.currency = (currency or DEFAULT_CURRENCY).upper()
        self.items = []
        self.subtotals = []
        self._subtotal = Decimal(0)
        self._delivery_charge = Decimal(0)
        self._total = Decimal(0)
        self.address = None
        self._delivery = None
        self._feature_type = None

    def _new_order(self, request: HttpRequest):
        """
        Start a new order
        :param request: http request
        """
        if not self.order_num or self.closed:
            if request and request.user.is_authenticated:
                self._initialise(self.currency)
                self.order_num = generate_order_num(request)
                self.user = request.user
                self.address = addresses_query(
                    user=self.user, address_type=AddressType.DEFAULT).first()
                self._delivery = get_delivery_product(
                    self.address.country,
                    del_type=ProductType.STANDARD_DELIVERY
                ).first() if self.address else None
                self._feature_type = None
                self.closed = False
            else:
                self.order_num = ''
                self.user = None
                self.closed = True

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

        self._calc_totals()

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
            self._calc_totals()
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
        self.closed = True
        self.add_to_request(request)

    def add_to_request(self, request: HttpRequest):
        """
        Add this basket to the request session.
        :param request: http request
        """
        if request:
            request.session[BASKET_SES] = self

    def calc_delivery(self, delivery_opt: OrderProduct) -> Decimal:
        """
        Calculate the current basket delivery charge for the specified option
        :param delivery_opt: delivery option
        :return: charge
        """
        return Decimal(0) if not delivery_opt else calc_ccy_cost(
            delivery_opt.unit_price, delivery_opt.base_currency,
            self._currency, count=self.num_items, as_decimal=True)

    def _calc_totals(self):
        """ Calculate the current basket totals """
        total = Decimal(0)
        for index, item in enumerate(self.items):
            cost = item.cost(as_decimal=True)
            if item.currency != self._currency:
                cost = convert_forex(cost, item.currency, self._currency,
                                     factor=FINANCIAL_FACTOR,
                                     result_as=NumType.DECIMAL)
            self.subtotals[index] = format_amount_str(cost, self._currency)
            total += cost

        self._subtotal = total
        self._delivery_charge = self.calc_delivery(self._delivery)
        self._total = total + self._delivery_charge

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
            self._calc_totals()
        else:
            raise ValueError(f'Unsupported currency: {code}')

    @property
    def delivery(self) -> Optional[OrderProduct]:
        """ Get the delivery product of the basket """
        return self._delivery

    @delivery.setter
    def delivery(self, delivery_opt: Union[OrderProduct, int]):
        """
        Set the delivery option of the basket
        :param delivery_opt: delivery option or id of option
        """
        if isinstance(delivery_opt, int):
            delivery_opt = get_object_or_404(OrderProduct, **{
                f'{OrderProduct.id_field()}': delivery_opt
            })

        if delivery_opt.type in list(
                map(lambda opt: opt.choice, ProductType.delivery_options())):
            self._delivery = delivery_opt
            self._calc_totals()
        else:
            raise ValueError(f'Invalid delivery option: {delivery_opt}')

    @property
    def feature_type(self) -> Optional[FeatureType]:
        """ Get the free delivery feature type of the basket """
        return self._feature_type

    @feature_type.setter
    def feature_type(self, f_type: Union[FeatureType, str]):
        """
        Set the free delivery feature type of the basket
        :param f_type: feature type or choice representing feature type
        """
        self._feature_type = FeatureType.from_choice(f_type) \
            if isinstance(f_type, str) else f_type

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
            self._calc_totals()
            success = True

        return success

    @property
    def subtotal(self) -> float:
        """
        The current basket subtotal (excluding delivery) in basket currency
        for display purposes
        """
        return normalise_amount(self._subtotal, self._currency)

    @property
    def subtotal_base_ccy(self) -> float:
        """
        The current basket subtotal (including delivery) in base currency
        for display purposes
        """
        return convert_forex(self._subtotal, self._currency, DEFAULT_CURRENCY,
                             factor=PRICING_FACTOR, result_as=NumType.FLOAT)

    @property
    def delivery_charge(self) -> float:
        """
        The current basket delivery charge in basket currency for display
        purposes
        """
        return normalise_amount(self._delivery_charge, self._currency)

    @property
    def total(self) -> float:
        """
        The current basket total (including delivery) in basket currency
        for display purposes
        """
        return normalise_amount(self._total, self._currency)

    @property
    def total_base_ccy(self) -> float:
        """
        The current basket total (including delivery) in base currency
        for display purposes
        """
        return convert_forex(self._total, self._currency, DEFAULT_CURRENCY,
                             factor=PRICING_FACTOR, result_as=NumType.FLOAT)

    @property
    def subtotal_str(self):
        """
        Formatted basket subtotal (excluding delivery) amount string
        (excluding currency)
        """
        return format_amount_str(self.subtotal, self._currency)

    @property
    def delivery_charge_str(self):
        """
        Formatted basket delivery charge amount string (excluding currency)
        """
        return format_amount_str(self.subtotal, self._currency)

    @property
    def total_str(self):
        """
        Formatted basket total (including delivery) amount string
        (excluding currency)
        """
        return format_amount_str(self.total, self._currency)

    def format_subtotal_str(self, with_symbol: bool = False):
        """
        Get a formatted basket subtotal (excluding delivery) amount string
        :param with_symbol: include currency symbol flag; default False
        :return: formatted string
        """
        return format_amount_str(self.subtotal, self._currency,
                                 with_symbol=with_symbol)

    def format_delivery_charge_str(self, with_symbol: bool = False,
                                   delivery_opt: OrderProduct = None):
        """
        Get a formatted basket delivery charge amount string
        :param with_symbol: include currency symbol flag; default False
        :param delivery_opt: delivery option; default current basket setting
        :return: formatted string
        """
        charge = self.delivery_charge if delivery_opt is None else \
            self.calc_delivery(delivery_opt)
        return format_amount_str(charge, self._currency,
                                 with_symbol=with_symbol)

    def format_total_str(self, with_symbol: bool = False):
        """
        Get a formatted basket total (including delivery) amount string
        :param with_symbol: include currency symbol flag; default False
        :return: formatted string
        """
        return format_amount_str(self.total, self._currency,
                                 with_symbol=with_symbol)

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
            'subtotal': self.subtotal,
            'delivery': self.total - self.subtotal,
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
    if new_order:
        basket = Basket(request=request)
    else:
        session_attrib = request.session[BASKET_SES]
        basket = session_attrib if isinstance(session_attrib, Basket) else \
            Basket.from_jsonable(session_attrib)
    basket.add_to_request(request)
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
        BASKET_ITEM_COUNT_CTX: 0 if basket.closed else basket.num_items
        if basket.num_items <= MAX_DISPLAY_COUNT else f'{MAX_DISPLAY_COUNT}+',
        BASKET_TOTAL_CTX: basket.format_subtotal_str(with_symbol=True)
    }
