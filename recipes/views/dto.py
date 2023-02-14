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
from dataclasses import dataclass, field
from datetime import timedelta
from typing import List

from django.utils.text import slugify

from base.dto import BaseDto
from recipes.views.recipe_queries import (
    get_recipe_instructions, get_recipe_ingredients_list, get_recipe
)
from recipes.models import (
    Recipe, RecipeIngredient
)


@dataclass
class IngredientDto(BaseDto):
    """ Recipe ingredient data transfer object """

    measure: str = ''

    @staticmethod
    def from_model(ingredient: RecipeIngredient):
        """
        Generate a DTO from the specified `ingredient`
        :param ingredient: model instance to populate DTO from
        :return: DTO instance
        """
        dto = BaseDto.from_model_to_obj(ingredient, IngredientDto())
        # custom handling for specific attributes
        dto.ingredient = ingredient.ingredient.name
        dto.measure = ingredient.ingredient.measure.abbrev

        return dto


@dataclass
class RecipeDto(BaseDto):
    """ Recipe data transfer object """

    _total_time: timedelta = timedelta()
    _alternatives: list[bool] = field(default_factory=list)

    @staticmethod
    def from_model(recipe: Recipe, *args, all_attrib: bool = True):
        """
        Generate a DTO from the specified `recipe`
        :param recipe: model instance to populate DTO from
        :param args: list of Recipe.xxx_FIELD names to populate in addition
                    to basic fields
        :param all_attrib: populate all attributes flag; default True
        :return: DTO instance
        """
        dto = BaseDto.from_model_to_obj(recipe, RecipeDto())
        # custom handling for specific attributes

        if all_attrib or Recipe.INGREDIENTS_FIELD in args:
            dto.ingredients = \
                list(map(IngredientDto.from_model,
                         list(recipe.recipeingredient_set.order_by(
                              RecipeIngredient.INDEX_FIELD).all()))
                     )
            num_ingredients = len(dto.ingredients)
            dto._alternatives = list(
                map(lambda _: False, range(num_ingredients)))
            for idx in range(len(dto.ingredients) - 1):
                alt_idx = idx + 1
                dto._alternatives[alt_idx] = \
                    dto.ingredients[alt_idx].index == \
                    dto.ingredients[idx].index

        if all_attrib or Recipe.INSTRUCTIONS_FIELD in args:
            dto.instructions = get_recipe_instructions(dto.id)
        if all_attrib or Recipe.IMAGES_FIELD in args:
            dto.images = list(recipe.image_set.all())
        if all_attrib or Recipe.AUTHOR_FIELD in args:
            dto.author = recipe.author

        return dto

    @staticmethod
    def from_id(pk: int, *args, all_attrib: bool = True):
        """
        Generate a DTO from the specified recipe `id`
        :param pk: recipe id to populate DTO from
        :param args: list of Recipe.xxx_FIELD names to populate in addition
                    to basic fields
        :param all_attrib: populate all attributes flag; default True
        :return: DTO instance
        """
        recipe, _ = get_recipe(pk)
        return RecipeDto.from_model(recipe, *args, all_attrib=all_attrib)

    @property
    def total_time(self) -> timedelta:
        """ Total cook and prep time """
        self._total_time = self.cook_time + self.prep_time
        return self._total_time

    @total_time.setter
    def total_time(self, time: timedelta):
        """ Set total cook and prep time """
        self._total_time = time

    @property
    def alternatives(self) -> List[bool]:
        """
        Alternative ingredients flags; True if entry is alternative for
        previous entry in ingredient list
        """
        return self._alternatives

    @property
    def display_order(self):
        """ Field values in display order """
        order = [
            getattr(self, key) for key in [
                Recipe.NAME_FIELD
            ]
        ]
        # amt = RecipeForm.quantise_amount(
        #     getattr(self, Recipe.AMOUNT_FIELD))
        # code = getattr(self, Recipe.BASE_CURRENCY_FIELD)
        # freq_type = getattr(self, Recipe.FREQUENCY_TYPE_FIELD)
        # freq = getattr(self, Recipe.FREQUENCY_FIELD)
        # assert freq_type is not None
        # order.append(f'{amt} {code} per {freq} {freq_type.value.name}')

        return order

    @property
    def main_image(self) -> str:
        """
        The url for the main image
        :return: url str or None
        """
        return self.images[0].url if len(self.images) > 0 else None

    @property
    def food_dot_com_url(self) -> str:
        """
        The url for the recipe on food.com
        :return: url str
        """
        return f'https://www.food.com/recipe/' \
               f'{slugify(self.name)}-{self.food_id}'
