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
from typing import List, Union, TypeVar
import re

from cloudinary.models import CloudinaryField
from django.db.models.fields.files import ImageFieldFile
from django.utils.text import slugify

from base.dto import BaseDto, ImagePool
from recipes.views.recipe_queries import (
    get_recipe_instructions, get_recipe
)
from recipes.models import (
    Recipe, RecipeIngredient, Instruction
)
from recipes.images import recipe_main_image, recipe_image_pool
from recipesnstuff import DEVELOPMENT
from utils import html_tag

TypeRecipeDto = TypeVar("TypeRecipeDto", bound="RecipeDto")


@dataclass
class IngredientDto(BaseDto):
    """ Recipe ingredient data transfer object """

    measure: str = ''

    @staticmethod
    def from_model(recipe_ingredient: RecipeIngredient):
        """
        Generate a DTO from the specified `recipe_ingredient`
        :param recipe_ingredient: model instance to populate DTO from
        :return: DTO instance
        """
        dto = BaseDto.from_model_to_obj(recipe_ingredient, IngredientDto())
        # custom handling for specific attributes
        dto.ingredient = recipe_ingredient.ingredient.name
        # Note: using measure from RecipeIngredient NOT Ingredient
        dto.measure = recipe_ingredient.measure.abbrev

        return dto

    def __str__(self) -> str:
        return f'{self.ingredient} {self.quantity} {self.measure}'


@dataclass
class InstructionDto(BaseDto):
    """ Recipe instruction data transfer object """

    @staticmethod
    def from_model(instruction: Instruction):
        """
        Generate a DTO from the specified `instruction`
        :param instruction: model instance to populate DTO from
        :return: DTO instance
        """
        dto = BaseDto.from_model_to_obj(instruction, IngredientDto())
        # custom handling for specific attributes
        return dto


@dataclass
class AverageRequirement:
    """
    Class representing average daily nutritional requirements
    ** Note: field names match Recipe model's field names **
    """
    calories: int
    fat_content: float
    saturated_fat_content: float
    cholesterol_content: float
    sodium_content: float
    carbohydrate_content: float
    fibre_content: float
    sugar_content: float
    protein_content: float


# Based on data from,
# 'Daily Value on the New Nutrition and Supplement Facts Labels'
# https://www.fda.gov/food/new-nutrition-facts-label/daily-value-new-nutrition-and-supplement-facts-labels
# U.S. Food and Drug Administration, https://www.fda.gov/
ADULT_DV = AverageRequirement(
    calories=2000, fat_content=78, saturated_fat_content=20,
    cholesterol_content=300, sodium_content=2300,
    carbohydrate_content=275, fibre_content=28, sugar_content=50,
    protein_content=50
)

NUTRI_FIELDS = {
    Recipe.CALORIES_FIELD: f'{html_tag("strong", "Calories")}: <<calories>>',
    Recipe.FAT_CONTENT_FIELD: 'Total Fat: <<fat_content>> g',
    Recipe.SATURATED_FAT_CONTENT_FIELD:
        'Saturated Fat: <<saturated_fat_content>> g',
    Recipe.CHOLESTEROL_CONTENT_FIELD:
        f'{html_tag("strong", "Cholesterol")}: <<cholesterol_content>> mg',
    Recipe.SODIUM_CONTENT_FIELD:
        f'{html_tag("strong", "Sodium")}: <<sodium_content>> mg',
    Recipe.CARBOHYDRATE_CONTENT_FIELD:
        f'{html_tag("strong", "Total Carbohydrate")}: '
        f'<<carbohydrate_content>> g',
    Recipe.FIBRE_CONTENT_FIELD: 'Dietary Fibre: <<fibre_content>> g',
    Recipe.SUGAR_CONTENT_FIELD: 'Sugars: <<sugar_content>> g',
    Recipe.PROTEIN_CONTENT_FIELD:
        f'{html_tag("strong", "Protein")}: <<protein_content>> g'
}
NUTRI_REGEX = re.compile(r'<<.*>>', re.IGNORECASE)


@dataclass
class RecipeDto(BaseDto):
    """ Recipe data transfer object """

    _total_time: timedelta = timedelta()
    _ingredient_alts: list[bool] = field(default_factory=list)
    """ Ingredient alternatives flags """
    _instruction_alts: list[bool] = field(default_factory=list)
    """ Instruction alternatives flags """

    @staticmethod
    def from_model(recipe: Recipe, *args, all_attrib: bool = True,
                   nutri_text: bool = False):
        """
        Generate a DTO from the specified `recipe`
        :param recipe: model instance to populate DTO from
        :param args: list of Recipe.xxx_FIELD names to populate in addition
                    to basic fields
        :param all_attrib: populate all attributes flag; default True
        :param nutri_text: generate nutritional info texts; default False
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
            dto._ingredient_alts = scan_alternatives(
                dto.ingredients, RecipeIngredient.INDEX_FIELD)
        if all_attrib or Recipe.INSTRUCTIONS_FIELD in args:
            dto.instructions = get_recipe_instructions(dto.id)
            dto._instruction_alts = scan_alternatives(
                dto.instructions, Instruction.INDEX_FIELD)
        if all_attrib or Recipe.IMAGES_FIELD in args:
            _images = [] if RecipeDto.has_no_uploaded_picture(
                recipe.picture) else [recipe.picture]
            _images.extend(list(recipe.image_set.all()))
            dto.images = _images
        if all_attrib or Recipe.AUTHOR_FIELD in args:
            dto.author = recipe.author
        if all_attrib or Recipe.CATEGORY_FIELD in args:
            dto.category = recipe.category

        if nutri_text:
            dto.daily_values = ADULT_DV
            dto.nutrition_list = []
            for fld in Recipe.nutritional_fields():
                nutri = round(getattr(dto, fld))
                nutri_text = re.sub(NUTRI_REGEX, str(nutri),
                                    NUTRI_FIELDS[fld])
                percent = round(nutri * 100 / getattr(ADULT_DV, fld))
                dto.nutrition_list.append(
                    (nutri_text, f'<strong>{percent}%</strong>')
                )

        return dto

    @staticmethod
    def from_id(pk: int, *args, all_attrib: bool = True,
                nutri_text: bool = False):
        """
        Generate a DTO from the specified recipe `id`
        :param pk: recipe id to populate DTO from
        :param args: list of Recipe.xxx_FIELD names to populate in addition
                    to basic fields
        :param all_attrib: populate all attributes flag; default True
        :param nutri_text: generate nutritional info texts; default False
        :return: DTO instance
        """
        recipe, _ = get_recipe(pk)
        return RecipeDto.from_model(recipe, *args, all_attrib=all_attrib,
                                    nutri_text=nutri_text)

    @staticmethod
    def has_no_uploaded_picture(
            picture: Union[ImageFieldFile, CloudinaryField]):
        # pristine has no name and name is 'False' if the image was cleared
        no_uploaded = True
        if picture:
            if DEVELOPMENT:     # ImageFieldFile
                no_uploaded = not picture.name or \
                              picture.name.lower() == 'false'
            else:
                no_uploaded = picture.public_id is not None
        return no_uploaded

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
    def ingredient_alts(self) -> List[bool]:
        """
        Alternative ingredients flags; True if entry is alternative for
        previous entry in ingredient list
        """
        return self._ingredient_alts

    @property
    def instruction_alts(self) -> List[bool]:
        """
        Alternative instructions flags; True if entry is alternative for
        previous entry in instruction list
        """
        return self._instruction_alts

    @property
    def display_order(self):
        """ Field values in display order """
        order = [
            getattr(self, key) for key in [
                Recipe.NAME_FIELD
            ]
        ]
        return order

    @property
    def main_image(self) -> ImagePool:
        """
        An image pool with just the main image
        :return: ImagePool
        """
        return recipe_main_image(self.images)

    @property
    def carousel(self) -> ImagePool:
        """
        An image pool with all images
        :return: ImagePool
        """
        return recipe_image_pool(self.images)

    @property
    def food_dot_com_url(self) -> str:
        """
        The url for the recipe on food.com
        :return: url str
        """
        return f'https://www.food.com/recipe/' \
               f'{slugify(self.name)}-{self.food_id}' if self.food_id else ''


def scan_alternatives(entities: List[Union[Instruction, RecipeIngredient]],
                      attrib: str) -> List[bool]:
    """
    Scan a list for alternatives
    :param entities: list to scan
    :param attrib: attrib to compare
    :return: list of alternatives
    """
    num_entities = len(entities)
    alts = list(
        map(lambda _: False, range(num_entities)))
    for idx in range(num_entities - 1):
        alt_idx = idx + 1
        alts[alt_idx] = \
            getattr(entities[alt_idx], attrib) == \
            getattr(entities[idx], attrib)

    return alts


@dataclass
class CategoryDto(BaseDto):
    """ Recipe data transfer object """

    @staticmethod
    def from_model(recipe: Recipe, *args):
        """
        Generate a DTO from the specified `recipe`
        :param recipe: model instance to populate DTO from
        :param args: list of Recipe.xxx_FIELD names to populate in addition
                    to basic fields
        :return: DTO instance
        """
        dto = BaseDto.from_model_to_obj(recipe, CategoryDto())
        # custom handling for specific attributes
        return dto

    @staticmethod
    def from_id(pk: int, *args):
        """
        Generate a DTO from the specified recipe `id`
        :param pk: recipe id to populate DTO from
        :param args: list of Recipe.xxx_FIELD names to populate in addition
                    to basic fields
        :return: DTO instance
        """
        recipe, _ = get_recipe(pk)
        return CategoryDto.from_model(recipe, *args,)
