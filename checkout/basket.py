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
from typing import List, Union, TypeVar, Tuple
from dataclasses import dataclass
from decimal import Decimal

from django.http import HttpRequest
import json_fix
import jsonpickle

from checkout.constants import BASKET_SES
from checkout.currency import is_valid_code, get_currency
from checkout.forex import NumType, convert_forex, normalise_amount
from order.misc import generate_order_num
from order.queries import get_subscription_product
from recipesnstuff.settings import FINANCIAL_FACTOR, DEFAULT_CURRENCY
from subscription.models import Subscription
from user.models import User

# workaround for self type hints from https://peps.python.org/pep-0673/
TypeBasketItem = TypeVar("TypeBasketItem", bound="BasketItem")
TypeBasket = TypeVar("TypeBasket", bound="Basket")


@dataclass
class BasketItem:
    """ Class representing an entry in the payment basket """
    currency: str
    amount: Union[int, float, Decimal]
    count: int
    description: str
    sku: str
    instructions: str

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
    def format_amount_str(amt: float, code: str):
        currency = get_currency(code)
        return f'{amt:.{currency.digits}f}'

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
    ATTRIB_instructions = 'instructions'

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
    _currency: str
    items: List[BasketItem]
    subtotals: List[float]
    _total: Decimal
    order_num: str
    user: User

    def __init__(self, currency: str = None, request: HttpRequest = None):
        self._initialise(currency)
        if request:
            self.order_num = generate_order_num(request)
            self.user = request.user
        else:
            self.order_num = ''
            self.user = None

    def _initialise(self, currency: str):
        """
        Initialise the basket
        :param currency: basket currency code
        """
        self._currency = currency if currency else DEFAULT_CURRENCY
        self.items = []
        self.subtotals = []
        self._total = Decimal.from_float(0)

    def add(self, amount: Union[int, float, Decimal], description: str,
            count: int = 1, sku: str = None, currency: str = None,
            instructions: str = None):
        """
        Add an item to the basket
        :param amount: cost per item
        :param description: description
        :param count: number of items
        :param sku: stock keeping unit; default None
        :param currency: currency code; default None i.e. basket currency
        :param instructions: additional instructions; default None
        """
        self.items.append(
            BasketItem(
                currency=currency if currency else self._currency,
                amount=amount, count=count, description=description,
                sku=sku, instructions=instructions
            )
        )
        self.subtotals.append(0)
        self._calc_total()

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

    def clear(self):
        """
        Clear the basket
        """
        self._initialise(self._currency)

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
        return len(self.items)

    @property
    def currency(self):
        """ Get the currency code of the basket """
        return self._currency.upper()

    @currency.setter
    def currency(self, currency: str):
        """
        Set the currency code of the basket
        :param currency: code to set
        """
        currency = currency.upper()
        if is_valid_code(currency):
            self._currency = currency
            self._calc_total()
        else:
            raise ValueError(f'Unsupported currency: {currency}')

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
    """
    basket, new_order = get_session_basket(request)

    order_prod = get_subscription_product(subscription)

    basket.add(
        subscription.amount, f"'{subscription.name}' subscription",
        count=count, sku=order_prod.sku, currency=subscription.base_currency,
        instructions=instructions
    )
