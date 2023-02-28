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
from enum import auto, Enum
from typing import TypeVar

from user.models import User
from utils import SortOrder, DESC_LOOKUP
from .models import Recipe, Category

# workaround for self type hints from https://peps.python.org/pep-0673/
TypeRecipeSortOrder = \
    TypeVar("TypeRecipeSortOrder", bound="RecipeSortOrder")


class RecipeQueryType(Enum):
    """ Enum representing different recipe query types """
    UNKNOWN = auto()
    RECIPES_BY_CATEGORY = auto()
    RECIPES_BY_AUTHOR = auto()
    ALL_RECIPES = auto()


class CategoryQueryType(Enum):
    """ Enum representing different category query types """
    UNKNOWN = auto()
    LETTER_CATEGORY = auto()
    ALL_CATEGORIES = auto()


UP_ARROWS = "\N{North East Arrow}"
DOWN_ARROWS = "\N{South East Arrow}"


class RecipeSortOrder(SortOrder):
    """ Enum representing recipe sort orders """
    NAME_AZ = (
        'Name A-Z', 'naz', f'{Recipe.NAME_FIELD}')
    NAME_ZA = (
        'Name Z-A', 'nza', f'{DESC_LOOKUP}{Recipe.NAME_FIELD}')
    PREP_TIME_LH = (
        f'Prep {UP_ARROWS}', 'p09', f'{Recipe.PREP_TIME_FIELD}')
    PREP_TIME_HL = (
        f'Prep {DOWN_ARROWS}', 'p90',
        f'{DESC_LOOKUP}{Recipe.PREP_TIME_FIELD}')
    COOK_TIME_LH = (
        f'Cook {UP_ARROWS}', 'c09', f'{Recipe.COOK_TIME_FIELD}')
    COOK_TIME_HL = (
        f'Cook {DOWN_ARROWS}', 'c90',
        f'{DESC_LOOKUP}{Recipe.COOK_TIME_FIELD}')
    TOTAL_TIME_LH = (
        f'Total {UP_ARROWS}', 't09', f'{Recipe.TOTAL_TIME_FIELD}')
    TOTAL_TIME_HL = (
        f'Total {DOWN_ARROWS}', 't90',
        f'{DESC_LOOKUP}{Recipe.TOTAL_TIME_FIELD}')
    AUTHOR_AZ = (
        'Author A-Z', 'aaz', f'{Recipe.AUTHOR_FIELD}__{User.USERNAME_FIELD}')
    AUTHOR_ZA = (
        'Author Z-A', 'aza',
        f'{DESC_LOOKUP}{Recipe.AUTHOR_FIELD}__{User.USERNAME_FIELD}')

    @classmethod
    def name_orders(cls) -> list[TypeRecipeSortOrder]:
        """ List of name-related sort orders """
        return [RecipeSortOrder.NAME_AZ, RecipeSortOrder.NAME_ZA]

    @property
    def is_name_order(self) -> bool:
        """ Check if this object is a name-related sort order """
        return self in self.name_orders()

    @classmethod
    def time_orders(cls) -> list[TypeRecipeSortOrder]:
        """ List of time-related sort orders """
        return [
            RecipeSortOrder.PREP_TIME_LH, RecipeSortOrder.PREP_TIME_HL,
            RecipeSortOrder.COOK_TIME_LH, RecipeSortOrder.COOK_TIME_HL,
            RecipeSortOrder.TOTAL_TIME_LH, RecipeSortOrder.TOTAL_TIME_HL,
        ]

    @property
    def is_time_order(self) -> bool:
        """ Check if this object is a time-related sort order """
        return self in self.time_orders()

    @classmethod
    def author_orders(cls) -> list[TypeRecipeSortOrder]:
        """ List of author-related sort orders """
        return [RecipeSortOrder.AUTHOR_AZ, RecipeSortOrder.AUTHOR_ZA]

    @property
    def is_author_order(self) -> bool:
        """ Check if this object is an author-related sort order """
        return self in self.author_orders()

    def to_field(self) -> str:
        """ Get Recipe field used for sorting """
        return Recipe.NAME_FIELD if self.is_name_order else \
            Recipe.AUTHOR_FIELD if self.is_author_order else \
            Recipe.PREP_TIME_FIELD if self in [
                RecipeSortOrder.PREP_TIME_LH, RecipeSortOrder.PREP_TIME_HL
            ] else Recipe.COOK_TIME_FIELD if self in [
                RecipeSortOrder.COOK_TIME_LH, RecipeSortOrder.COOK_TIME_HL
            ] else Recipe.TOTAL_TIME_FIELD


RecipeSortOrder.DEFAULT = RecipeSortOrder.NAME_AZ


class CategorySortOrder(SortOrder):
    """ Enum representing category sort orders """
    NAME_AZ = (
        'Name A-Z', 'naz', f'{Recipe.NAME_FIELD}')
    NAME_ZA = (
        'Name Z-A', 'nza', f'{DESC_LOOKUP}{Recipe.NAME_FIELD}')

    @classmethod
    def name_orders(cls) -> list[TypeRecipeSortOrder]:
        """ List of name-related sort orders """
        return [CategorySortOrder.NAME_AZ, CategorySortOrder.NAME_ZA]

    @property
    def is_name_order(self) -> bool:
        """ Check if this object is a name-related sort order """
        return self in self.name_orders()

    def to_field(self) -> str:
        """ Get Recipe field used for sorting """
        return Category.NAME_FIELD


CategorySortOrder.DEFAULT = CategorySortOrder.NAME_AZ
