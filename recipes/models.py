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
from typing import TypeVar
from decimal import Decimal
from datetime import timedelta, datetime, MINYEAR, timezone
import html

from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from user.models import User
from utils import ModelMixin

from .constants import (
    NAME_FIELD, TYPE_FIELD, SYSTEM_FIELD, IS_DEFAULT_FIELD, ABBREV_FIELD,
    BASE_US_FIELD, BASE_METRIC_FIELD, MEASURE_FIELD, FOOD_ID_FIELD, TEXT_FIELD,
    URL_FIELD, RECIPE_FIELD, PREP_TIME_FIELD, COOK_TIME_FIELD,
    TOTAL_TIME_FIELD, DATE_PUBLISHED_FIELD, DESCRIPTION_FIELD, CATEGORY_FIELD,
    KEYWORDS_FIELD, AUTHOR_FIELD, SERVINGS_FIELD, RECIPE_YIELD_FIELD,
    INGREDIENTS_FIELD, INSTRUCTIONS_FIELD, IMAGES_FIELD, CALORIES_FIELD,
    FAT_CONTENT_FIELD, SATURATED_FAT_CONTENT_FIELD, CHOLESTEROL_CONTENT_FIELD,
    SODIUM_CONTENT_FIELD, CARBOHYDRATE_CONTENT_FIELD, FIBRE_CONTENT_FIELD,
    SUGAR_CONTENT_FIELD, PROTEIN_CONTENT_FIELD, INGREDIENT_FIELD,
    QUANTITY_FIELD, INDEX_FIELD
)

# workaround for self type hints from https://peps.python.org/pep-0673/
TypeMeasure = TypeVar("TypeMeasure", bound="Measure")


class Category(ModelMixin, models.Model):
    """
    Category model
    """
    # field names
    NAME_FIELD = NAME_FIELD

    CATEGORY_ATTRIB_NAME_MAX_LEN: int = 50

    name = models.CharField(
        _('name'), max_length=CATEGORY_ATTRIB_NAME_MAX_LEN,
        blank=False, unique=True)

    @dataclass
    class Meta:
        """ Model metadata """

    def __str__(self):
        return f'{self.name}'


class Keyword(ModelMixin, models.Model):
    """
    Keyword model
    """
    # field names
    NAME_FIELD = NAME_FIELD

    KEYWORD_ATTRIB_NAME_MAX_LEN: int = 50

    name = models.CharField(
        _('name'), max_length=KEYWORD_ATTRIB_NAME_MAX_LEN,
        blank=False, unique=True)

    @dataclass
    class Meta:
        """ Model metadata """

    def __str__(self):
        return f'{self.name}'


class Measure(ModelMixin, models.Model):
    """
    Measure model
    """
    # field names
    TYPE_FIELD = TYPE_FIELD
    SYSTEM_FIELD = SYSTEM_FIELD
    IS_DEFAULT_FIELD = IS_DEFAULT_FIELD
    NAME_FIELD = NAME_FIELD
    ABBREV_FIELD = ABBREV_FIELD
    BASE_US_FIELD = BASE_US_FIELD
    BASE_METRIC_FIELD = BASE_METRIC_FIELD

    MEASURE_ATTRIB_NAME_MAX_LEN: int = 30
    MEASURE_ATTRIB_ABBREV_MAX_LEN: int = 20

    DRY_FLUID = 'df'
    WEIGHT = 'w'
    UNIT = 'u'
    TYPE_CHOICES = [
        (DRY_FLUID, 'Dry/fluid'),
        (WEIGHT, 'Weight'),
        (UNIT, 'Unit'),
    ]
    SYSTEM_US = 'us'
    SYSTEM_METRIC = 'si'
    SYSTEM_ONE = '1'
    SYSTEM_CHOICES = [
        (SYSTEM_US, 'US'),
        (SYSTEM_METRIC, 'Metric'),
        (SYSTEM_ONE, 'Dimensionless'),
    ]

    type = models.CharField(
        max_length=2, choices=TYPE_CHOICES, default=DRY_FLUID, help_text=_(
            "Designates the type of measurement."
        )
    )
    system = models.CharField(
        # default is US since the sample recipes use US measures
        max_length=2, choices=SYSTEM_CHOICES, default=SYSTEM_US, help_text=_(
            "Designates the measurement system."
        )
    )
    is_default = models.BooleanField(
        default=False, blank=False, help_text=_(
            "Designates the default measurement for the system and type."
        )
    )
    name = models.CharField(
        _('name'), max_length=MEASURE_ATTRIB_NAME_MAX_LEN, unique=True)
    abbrev = models.CharField(
        _('abbreviation'), max_length=MEASURE_ATTRIB_ABBREV_MAX_LEN)

    # Measurement values are defined in terms of a base US unit
    # (since recipe data was given in US units) and metric.
    # Dry/fluid base unit is fl. oz. and weight is oz.
    # Values taken from
    # https://en.wikipedia.org/wiki/Cooking_weights_and_measures#British_(Imperial)_measures
    # https://en.wikipedia.org/wiki/United_States_customary_units
    base_us = models.DecimalField(
        max_digits=19, decimal_places=10, default=1.0)
    base_metric = models.DecimalField(
        max_digits=19, decimal_places=10, default=1.0)

    @property
    def base_system(self) -> Decimal:
        """ Conversion factor to system base unit """
        return self.other_system(self)

    def other_system(self, measure: TypeMeasure) -> Decimal:
        """
        Conversion factor to another system base unit
        :param measure: measure for which conversion factor is needed
        :return:
        """
        # doesn't matter which base used for SYSTEM_ONE as they're the same
        return self.base_metric if measure.system == Measure.SYSTEM_METRIC \
            else self.base_us

    @dataclass
    class Meta:
        """ Model metadata """

    @classmethod
    def _get_default_instance(
            cls, name: str, abbrev: str, measure_type: str,
            system: str) -> TypeMeasure:
        """
        Get a default instance for objects requiring a Measure field
        :param name: measure name
        :param abbrev: abbreviation
        :param measure_type: type of unit
        :param system: measurement system
        :return: default instance
        """
        default_inst, _ = cls.objects.get_or_create(**{
                f'{Measure.NAME_FIELD}': name,
            },
            defaults={
                f'{Measure.TYPE_FIELD}': measure_type,
                f'{Measure.ABBREV_FIELD}': abbrev,
                f'{Measure.SYSTEM_FIELD}': system,
                f'{Measure.IS_DEFAULT_FIELD}': True,
                f'{Measure.BASE_US_FIELD}': 1.0,
                f'{Measure.BASE_METRIC_FIELD}': 1.0,
            },
        )
        return default_inst

    @classmethod
    def get_default_unit(cls) -> TypeMeasure:
        """ Get the default pk for objects requiring a Measure field """
        return cls._get_default_instance(
            'unit', '', Measure.UNIT, Measure.SYSTEM_ONE)

    @classmethod
    def get_default_us_dry_fluid(cls) -> TypeMeasure:
        """
        Get the default US base unit for objects requiring a dry/fluid
        Measure field
        """
        return cls._get_default_instance(
            'fluid ounce', 'fl. oz.', Measure.DRY_FLUID, Measure.SYSTEM_US)

    @classmethod
    def get_default_us_weight(cls) -> TypeMeasure:
        """
        Get the default US base unit for objects requiring a weight
        Measure field
        """
        return cls._get_default_instance(
            'ounce', 'oz.', Measure.WEIGHT, Measure.SYSTEM_US)

    @classmethod
    def get_default_metric_dry_fluid(cls) -> TypeMeasure:
        """
        Get the default US base unit for objects requiring a dry/fluid
        Measure field
        """
        return cls._get_default_instance(
            'decilitre', 'dl', Measure.DRY_FLUID, Measure.SYSTEM_METRIC)

    @classmethod
    def get_default_metric_weight(cls) -> TypeMeasure:
        """
        Get the default US base unit for objects requiring a weight
        Measure field
        """
        return cls._get_default_instance(
            'gram', 'g', Measure.WEIGHT, Measure.SYSTEM_METRIC)

    def __str__(self):
        return f'{self.name}'


class Ingredient(ModelMixin, models.Model):
    """
    Ingredient model
    """
    # field names
    NAME_FIELD = NAME_FIELD
    MEASURE_FIELD = MEASURE_FIELD

    KEYWORD_ATTRIB_NAME_MAX_LEN: int = 75

    name = models.CharField(
        _('name'), max_length=KEYWORD_ATTRIB_NAME_MAX_LEN,
        blank=False, unique=True)

    measure = models.ForeignKey(
        Measure, on_delete=models.CASCADE, help_text=_(
            "Designates the standard measure for the ingredient."
        )
    )

    @dataclass
    class Meta:
        """ Model metadata """

    def __str__(self):
        return f'{html.unescape(self.name)} ({self.measure.name})'


class Instruction(ModelMixin, models.Model):
    """
    Ingredient model
    """
    # field names
    TEXT_FIELD = TEXT_FIELD

    INSTRUCTION_ATTRIB_TEXT_MAX_LEN: int = 3000

    text = models.CharField(
        _('text'), max_length=INSTRUCTION_ATTRIB_TEXT_MAX_LEN,
        blank=False)

    @dataclass
    class Meta:
        """ Model metadata """

    def __str__(self):
        return f'{self.text}'


class Recipe(ModelMixin, models.Model):
    """
    Recipe model
    """
    # field names
    NAME_FIELD = NAME_FIELD
    FOOD_ID_FIELD = FOOD_ID_FIELD
    PREP_TIME_FIELD = PREP_TIME_FIELD
    COOK_TIME_FIELD = COOK_TIME_FIELD
    TOTAL_TIME_FIELD = TOTAL_TIME_FIELD     # sum of prep & cook annotation
    DATE_PUBLISHED_FIELD = DATE_PUBLISHED_FIELD
    DESCRIPTION_FIELD = DESCRIPTION_FIELD
    CATEGORY_FIELD = CATEGORY_FIELD
    KEYWORDS_FIELD = KEYWORDS_FIELD
    AUTHOR_FIELD = AUTHOR_FIELD
    SERVINGS_FIELD = SERVINGS_FIELD
    RECIPE_YIELD_FIELD = RECIPE_YIELD_FIELD
    INGREDIENTS_FIELD = INGREDIENTS_FIELD
    INSTRUCTIONS_FIELD = INSTRUCTIONS_FIELD
    IMAGES_FIELD = IMAGES_FIELD             # image set
    CALORIES_FIELD = CALORIES_FIELD
    FAT_CONTENT_FIELD = FAT_CONTENT_FIELD
    SATURATED_FAT_CONTENT_FIELD = SATURATED_FAT_CONTENT_FIELD
    CHOLESTEROL_CONTENT_FIELD = CHOLESTEROL_CONTENT_FIELD
    SODIUM_CONTENT_FIELD = SODIUM_CONTENT_FIELD
    CARBOHYDRATE_CONTENT_FIELD = CARBOHYDRATE_CONTENT_FIELD
    FIBRE_CONTENT_FIELD = FIBRE_CONTENT_FIELD
    SUGAR_CONTENT_FIELD = SUGAR_CONTENT_FIELD
    PROTEIN_CONTENT_FIELD = PROTEIN_CONTENT_FIELD

    RECIPE_ATTRIB_NAME_MAX_LEN: int = 100
    RECIPE_ATTRIB_DESC_MAX_LEN: int = 10000
    RECIPE_ATTRIB_YIELD_MAX_LEN: int = 100

    name = models.CharField(
        _('name'), max_length=RECIPE_ATTRIB_NAME_MAX_LEN, blank=False)

    food_id = models.BigIntegerField(
        default=0, help_text=_("the id of the recipe from Food.com.")
    )

    prep_time = models.DurationField(
        _('preparation time'), default=timedelta())

    cook_time = models.DurationField(
        _('cooking time'), default=timedelta())

    date_published = models.DateTimeField(
        _('date published'),
        default=datetime(MINYEAR, 1, 1, tzinfo=timezone.utc))

    description = models.CharField(
        _('description'), max_length=RECIPE_ATTRIB_DESC_MAX_LEN)

    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    keywords = models.ManyToManyField(Keyword)

    author = models.ForeignKey(User, on_delete=models.CASCADE)

    servings = models.IntegerField(
        _('number of servings'), default=0)

    recipe_yield = models.CharField(
        _('recipe yield'), max_length=RECIPE_ATTRIB_YIELD_MAX_LEN)

    ingredients = models.ManyToManyField(
        Ingredient, through='RecipeIngredient')

    instructions = models.ManyToManyField(Instruction)

    calories = models.FloatField(_('calories'), default=0)
    fat_content = models.FloatField(_('fat content'), default=0)
    saturated_fat_content = models.FloatField(
        _('saturated fat content'), default=0)
    cholesterol_content = models.FloatField(
        _('cholesterol content'), default=0)
    sodium_content = models.FloatField(_('sodium content'), default=0)
    carbohydrate_content = models.FloatField(
        _('carbohydrate content'), default=0)
    fibre_content = models.FloatField(_('fibre content'), default=0)
    sugar_content = models.FloatField(_('sugar content'), default=0)
    protein_content = models.FloatField(_('protein content'), default=0)

    @dataclass
    class Meta:
        """ Model metadata """

    @classmethod
    def date_fields(cls) -> list[str]:
        return [Recipe.DATE_PUBLISHED_FIELD]

    @classmethod
    def timedelta_fields(cls) -> list[str]:
        return [
            Recipe.PREP_TIME_FIELD, Recipe.COOK_TIME_FIELD,
            Recipe.TOTAL_TIME_FIELD
        ]

    @classmethod
    def numeric_fields(cls) -> list[str]:
        return [
            Recipe.SERVINGS_FIELD, Recipe.CALORIES_FIELD,
            Recipe.FAT_CONTENT_FIELD, Recipe.SATURATED_FAT_CONTENT_FIELD,
            Recipe.CHOLESTEROL_CONTENT_FIELD, Recipe.SODIUM_CONTENT_FIELD,
            Recipe.CARBOHYDRATE_CONTENT_FIELD, Recipe.FIBRE_CONTENT_FIELD,
            Recipe.SUGAR_CONTENT_FIELD, Recipe.PROTEIN_CONTENT_FIELD
        ]

    def __str__(self):
        return f'{self.name}'


class RecipeIngredient(ModelMixin, models.Model):
    """
    Recipe ingredients model
    """

    RECIPE_FIELD = RECIPE_FIELD
    INGREDIENT_FIELD = INGREDIENT_FIELD
    QUANTITY_FIELD = QUANTITY_FIELD
    INDEX_FIELD = INDEX_FIELD

    RECIPE_INGREDIENT_ATTRIB_QUANTITY_MAX_LEN: int = 30
    RECIPE_INGREDIENT_ATTRIB_INDEX_MIN: int = 1
    RECIPE_INGREDIENT_ATTRIB_INDEX_MAX: int = 32767

    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantity = models.CharField(
        max_length=RECIPE_INGREDIENT_ATTRIB_QUANTITY_MAX_LEN)
    index = models.PositiveSmallIntegerField(
        _('index in ingredient list'),
        default=RECIPE_INGREDIENT_ATTRIB_INDEX_MIN,
        validators=[
            MinValueValidator(RECIPE_INGREDIENT_ATTRIB_INDEX_MIN),
            MaxValueValidator(RECIPE_INGREDIENT_ATTRIB_INDEX_MAX)
        ]
    )

    @dataclass
    class Meta:
        """ Model metadata """

    def __str__(self):
        return f'{self.index} {self.ingredient.name} - {self.recipe.name}'


class Image(ModelMixin, models.Model):
    """
    Image model
    """
    # field names
    URL_FIELD = URL_FIELD
    RECIPE_FIELD = RECIPE_FIELD

    IMAGE_ATTRIB_URL_MAX_LEN: int = 1000

    url = models.CharField(
        _('image url'), max_length=IMAGE_ATTRIB_URL_MAX_LEN,
        blank=False)

    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)

    @dataclass
    class Meta:
        """ Model metadata """

    def __str__(self):
        return f'{self.text}'
