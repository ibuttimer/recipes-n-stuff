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
import decimal
from contextvars import Context
from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from typing import Optional, Union, TypeVar

from .models import Measure


# workaround for self type hints from https://peps.python.org/pep-0673/
TypeQuantity = TypeVar("TypeQuantity", bound="Quantity")


class Measures(Enum):
    """ Enum represent measures """
    GALLON = ("gallon", "gal.")
    QUART = ("quart", "qt.")
    PINT = ("pint", "pt.")
    CUP = ("cup", "C")
    TEACUP = ("teacup", "tcf.")
    GILL = ("gill", "gi.")
    WINEGLASS = ("wineglass", "wgf.")
    FLUID_OUNCE = ("fluid ounce", "fl. oz.")
    TABLESPOON = ("tablespoon", "tbsp.")
    DESSERTSPOON = ("dessertspoon", "dsp.")
    TEASPOON = ("teaspoon", "tsp.")
    FLUID_DRAM = ("fluid dram", "fl. dr.")
    COFFEESPOON = ("coffeespoon", "csp.")
    SALTSPOON = ("saltspoon", "ssp.")
    DASH = ("dash", "ds.")
    PINCH = ("pinch", "pn.")
    SMIDGEN = ("smidgen", "smdg.")
    DROP = ("drop", "gt.")

    LITRE = ("litre", "l")
    MILLILITRE = ("millilitre", "ml")
    CENTILITRE = ("centilitre", "cl")
    DECILITRE = ("decilitre", "dl")

    DRAM = ("dram", "dr.")
    OUNCE = ("ounce", "oz.")
    POUND = ("pound", "lb.")
    STONE = ("stone", "st.")

    GRAM = ("gram", "g")
    KILOGRAM = ("kilogram", "kg")
    MILLIGRAM = ("milligram", "mg")

    UNIT = ("unit", "")


@dataclass
class Quantity:
    """ Class representing a quantity """
    measure: Measures
    amount: Union[int, float, Decimal]

    STD_PLACES = 3
    """ Standard number of decimal places """

    def convert_to(self, measure: Measures,
                   quantised: bool = False, places: int = STD_PLACES,
                   rounding: str | None = None,
                   context: Context | None = None) -> TypeQuantity:
        """
        Convert to the specified Measure
        :param measure: required measure
        :param quantised: quantised amount flag; default False
        :param places: number of decimal places; default 3
        :param rounding: rounding mode: default None
        :param context: context for arithmetic; default None
        :return: number rounded to exponent
        """
        quantity = convert(
            self.amount, self.measure, measure,
            quantised=quantised,
            places=places if quantised else Quantity.STD_PLACES,
            rounding=rounding, context=context
        )

        return Quantity(measure, quantity)

    @staticmethod
    def standardise(quantity: Union[TypeQuantity, Decimal, int, float],
                    places: int = STD_PLACES, rounding: str | None = None,
                    context: Context | None = None
                    ) -> Union[TypeQuantity, Decimal]:
        """
        Standardise a Quantity or Decimal
        :param quantity: object to standardise
        :param places: number of decimal places; default 3
        :param rounding: rounding mode: default None
        :param context: context for arithmetic; default None
        :return: new standardised object
        """
        if isinstance(quantity, Quantity):
            amount = quantity.amount
        else:
            amount = quantity \
                if isinstance(quantity, Decimal) else Decimal(quantity)
        amount = amount.quantize(
            Quantity.exp(places), rounding=rounding, context=context)
        return Quantity(quantity.measure, amount) \
            if isinstance(quantity, Quantity) else amount

    @staticmethod
    def quantised_of(measure: Measures, quantity: Union[int, float, Decimal],
                     places: int = STD_PLACES,
                     rounding: str | None = None,
                     context: Context | None = None) -> TypeQuantity:
        """
        Return a Quantity of `measure` with a value equal to `quantity` after
        rounding and having the exponent `exp`.
        Decimal('1.41421356').quantize(Decimal('1.000'))
             Decimal('1.414')
        :param measure: measure of quantity
        :param quantity: amount of quantity
        :param places: number of decimal places; default 3
        :param rounding: rounding mode: default None
        :param context: context for arithmetic; default None
        :return: number rounded to exponent
        """
        assert places >= 0
        return Quantity(measure, Decimal(quantity).quantize(
            Quantity.exp(places), rounding=rounding, context=context))

    @staticmethod
    def exp(places: int = STD_PLACES) -> Decimal:
        """
        Return an exponent
        :param places: number of decimal places; default 3
        :return: exponent
        """
        assert places >= 0
        # e.g. Decimal(10) ** -2       # same as Decimal('0.01')
        return Decimal(10) ** -places

# https://docs.python.org/3/library/decimal.html


def convert(
    from_q: Union[int, float, Decimal], from_t: Measures,
    to_t: Measures, quantised: bool = False,
    places: int = Quantity.STD_PLACES,
    rounding: str | None = None, context: Context | None = None
) -> Optional[Decimal]:
    """
    Convert a quantity
    :param from_q: amount to convert
    :param from_t: measure to convert from
    :param quantised: quantised amount flag; default False
    :param to_t: measure to convert to
    :param places: number of decimal places; default 3
    :param rounding: rounding mode: default None
    :param context: context for arithmetic; default None
    :return: converted quantity
    """
    conversion = None
    from_m = get_measure_by_name(from_t.value[0])
    to_m = get_measure_by_name(to_t.value[0])
    if from_m and to_m and from_m.type == to_m.type:
        to_places = Quantity.exp(places)

        if from_m.system == to_m.system:
            # same system; (from * from.base_system) / to.base_system
            conversion = (Decimal(from_q) * from_m.base_system) \
                         / to_m.base_system
        else:
            # different system;
            # (from * from.base_other_system) / to.base_system
            conversion = (Decimal(from_q) * from_m.other_system(to_m)) \
                         / to_m.base_system

        if quantised:
            conversion = conversion.quantize(
                to_places, rounding=rounding, context=context)

            if places > Quantity.STD_PLACES:
                # maths requires too much precision, rounding solves it
                conversion = Quantity.standardise(conversion)

    return conversion


def get_measure_by_name(name: str) -> Optional[Measure]:
    """
    Get a measure
    :param name: name of measure to get
    :return: measure or None
    """
    query = Measure.objects.filter(**{
        Measure.NAME_FIELD: name
    })
    return query.get() if query.count() == 1 else None
