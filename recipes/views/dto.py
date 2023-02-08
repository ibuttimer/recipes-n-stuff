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
from dataclasses import dataclass
from datetime import timedelta

from django.utils.text import slugify

from base.dto import BaseDto
from recipes.views.recipe_queries import (
    get_recipe_instructions, get_recipe_ingredients
)
from recipes.models import (
    Recipe
)


@dataclass
class RecipeDto(BaseDto):
    """ Recipe data transfer object """

    _total_time: timedelta = timedelta()

    @staticmethod
    def from_model(recipe: Recipe, *args, all_attrib: bool = True):
        """
        Generate a DTO from the specified `model`
        :param recipe: model instance to populate DTO from
        :param args: list of Recipe.xxx_FIELD names to populate in addition
                    to basic fields
        :param all_attrib: populate all attributes flag; default True
        :return: DTO instance
        """
        dto = BaseDto.from_model_to_obj(recipe, RecipeDto())
        # custom handling for specific attributes

        if all_attrib or Recipe.INGREDIENTS_FIELD in args:
            dto.ingredients = get_recipe_ingredients(dto.id)
        if all_attrib or Recipe.INSTRUCTIONS_FIELD in args:
            dto.instructions = get_recipe_instructions(dto.id)
        if all_attrib or Recipe.IMAGES_FIELD in args:
            dto.images = list(recipe.image_set.all())
        if all_attrib or Recipe.AUTHOR_FIELD in args:
            dto.author = recipe.author

        return dto

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
