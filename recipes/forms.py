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
from typing import Tuple, List

from cloudinary.forms import CloudinaryFileField
from django import forms
from django.core.exceptions import ValidationError
from django.forms import CharField
from django.utils.translation import gettext_lazy as _

from recipesnstuff import DEV_IMAGE_FILE_TYPES, DEVELOPMENT, IMAGE_FILE_TYPES
from user.forms import NoCurrentClearableFileInput
from utils import error_messages, ErrorMsgs, update_field_widgets, FormMixin

from .constants import (
    INGREDIENT_FIELD, QUANTITY_FIELD, INDEX_FIELD, TEXT_FIELD, MEASURE_FIELD
)
from .models import RecipeIngredient, Instruction, Measure, Recipe, Category
from .views.utils import parse_duration, DURATION_FORMAT_STR


class RecipeIngredientForm(forms.ModelForm):
    """
    Form to update a RecipeIngredient.
    """

    QUANTITY_FF = QUANTITY_FIELD
    INDEX_FF = INDEX_FIELD
    MEASURE_FF = MEASURE_FIELD

    quantity = forms.CharField(
        label=_("Quantity"),
        max_length=RecipeIngredient.RECIPE_INGREDIENT_ATTRIB_QUANTITY_MAX_LEN,
        required=True)

    index = forms.IntegerField(
        label=_("Index"),
        min_value=RecipeIngredient.RECIPE_INGREDIENT_ATTRIB_INDEX_MIN,
        max_value=RecipeIngredient.RECIPE_INGREDIENT_ATTRIB_INDEX_MAX,
        required=True)

    measure = forms.ModelChoiceField(
        queryset=Measure.objects.order_by(Measure.NAME_FIELD).all(),
        empty_label="Measure",
        required=True
    )

    @dataclass
    class Meta:
        """ Form metadata """
        model = RecipeIngredient
        fields = [
            INDEX_FIELD, QUANTITY_FIELD, MEASURE_FIELD
        ]
        non_bootstrap_fields = []
        select_fields = [MEASURE_FIELD]
        help_texts = {
            QUANTITY_FIELD: 'Quantity of ingredient.',
            INDEX_FIELD: 'Position in ingredient list, duplicates indicate '
                         'alternatives.',
            MEASURE_FIELD: 'Ingredient measure.'
        }

        @staticmethod
        def generate_error_messages():
            _msgs = [
                ErrorMsgs(
                    field, required=True,
                    max_length=RecipeIngredient.
                    RECIPE_INGREDIENT_ATTRIB_QUANTITY_MAX_LEN
                ) for field in (
                    QUANTITY_FIELD,
                )
            ]
            _msgs.extend([
                ErrorMsgs(
                    field, required=True
                ) for field in (
                    MEASURE_FIELD,
                )
            ])
            _msgs.extend([
                ErrorMsgs(
                    field, required=True,
                    max_value=RecipeIngredient.
                    RECIPE_INGREDIENT_ATTRIB_INDEX_MAX,
                    min_value=RecipeIngredient.
                    RECIPE_INGREDIENT_ATTRIB_INDEX_MIN
                ) for field in (
                    INDEX_FIELD,
                )
            ])
            return error_messages(RecipeIngredient.model_name_caps(), *_msgs)

        error_messages = generate_error_messages()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # add the bootstrap class to the widget
        update_field_widgets(
            self,
            # exclude non-bootstrap fields
            [field for field in RecipeIngredientForm.Meta.fields
             if field not in RecipeIngredientForm.Meta.non_bootstrap_fields
             and field not in RecipeIngredientForm.Meta.select_fields],
            {'class': 'form-control'})
        update_field_widgets(
            self, RecipeIngredientForm.Meta.select_fields,
            {'class': 'form-select'})


class RecipeIngredientNewForm(forms.ModelForm):
    """
    Form to create a RecipeIngredient.
    """

    INGREDIENT_FF = INGREDIENT_FIELD

    ingredient = forms.CharField(
        required=True, widget=forms.TextInput(attrs={
            'list': 'id__ingredient-datalist',
            'placeholder': 'Type to search...',
            'id': 'id__ingredient-input-new'
        })
    )

    @dataclass
    class Meta(RecipeIngredientForm.Meta):
        """ Form metadata """

        @staticmethod
        def extend() -> Tuple[List[str], List[str], dict, dict]:
            _fields = RecipeIngredientForm.Meta.fields.copy()
            _fields.append(INGREDIENT_FIELD)

            _select_fields = RecipeIngredientForm.Meta.select_fields.copy()

            _help_texts = RecipeIngredientForm.Meta.help_texts.copy()
            _help_texts[INGREDIENT_FIELD] = 'Ingredient.'

            _error_msgs = RecipeIngredientForm.Meta.error_messages.copy()
            _error_msgs.update(error_messages(
                RecipeIngredient.model_name_caps(),
                *[ErrorMsgs(
                    field, required=True, from_list=True
                ) for field in (
                    INGREDIENT_FIELD,
                )]
            ))

            return _fields, _select_fields, _help_texts, _error_msgs

        model = RecipeIngredient
        fields, select_fields, help_texts, error_messages = extend()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # add the bootstrap class to the widget
        update_field_widgets(
            self,
            # exclude non-bootstrap fields
            [field for field in RecipeIngredientNewForm.Meta.fields
             if field not in RecipeIngredientNewForm.Meta.non_bootstrap_fields
             and field not in RecipeIngredientNewForm.Meta.select_fields],
            {'class': 'form-control'})
        update_field_widgets(
            self,
            RecipeIngredientNewForm.Meta.select_fields,
            {'class': 'form-select'})


class RecipeInstructionForm(forms.ModelForm):
    """
    Form to update a recipe Instruction.
    """

    TEXT_FF = TEXT_FIELD
    INDEX_FF = INDEX_FIELD

    text = forms.CharField(
        label=_("Text"),
        max_length=Instruction.INSTRUCTION_ATTRIB_TEXT_MAX_LEN,
        required=True)

    index = forms.IntegerField(
        label=_("Index"),
        min_value=Instruction.INSTRUCTION_ATTRIB_INDEX_MIN,
        max_value=Instruction.INSTRUCTION_ATTRIB_INDEX_MAX,
        required=True)

    @dataclass
    class Meta:
        """ Form metadata """
        model = Instruction
        fields = [
            INDEX_FIELD,
            TEXT_FIELD
        ]
        non_bootstrap_fields = []
        select_fields = []
        help_texts = {
            TEXT_FIELD: 'Instruction text.',
            INDEX_FIELD: 'Position in ingredient list, duplicates indicate '
                         'alternatives.',
        }

        @staticmethod
        def generate_error_messages():
            msgs = error_messages(
                Instruction.model_name_caps(),
                *[ErrorMsgs(
                    field, required=True,
                    max_length=Instruction.INSTRUCTION_ATTRIB_TEXT_MAX_LEN
                ) for field in (
                    TEXT_FIELD,
                )]
            )
            msgs.update(error_messages(
                Instruction.model_name_caps(),
                *[ErrorMsgs(
                    field, required=True,
                    max_value=Instruction.INSTRUCTION_ATTRIB_INDEX_MAX,
                    min_value=Instruction.INSTRUCTION_ATTRIB_INDEX_MIN
                ) for field in (
                    INDEX_FIELD,
                )]
            ))
            return msgs

        error_messages = generate_error_messages()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # add the bootstrap class to the widget
        update_field_widgets(
            self,
            # exclude non-bootstrap fields
            [field for field in RecipeInstructionForm.Meta.fields
             if field not in RecipeInstructionForm.Meta.non_bootstrap_fields
             and field not in RecipeInstructionForm.Meta.select_fields],
            {'class': 'form-control'})
        update_field_widgets(
            self,
            RecipeInstructionForm.Meta.select_fields,
            {'class': 'form-select'})


def validate_duration(value) -> timedelta:
    """
    Validate duration strings
    :param value: string to validate
    :raises: ValidationError if fails validation
    """
    is_valid, duration = parse_duration(value)
    if not is_valid:
        raise ValidationError(
            _('%(value)s is not a valid duration. Correct format is %(fmt)s.'),
            params={'value': value, 'fmt': DURATION_FORMAT_STR},
        )
    return duration


class CategoryCharField(CharField):
    """ Custom CharField to return Category from name entered """
    def to_python(self, value):
        """Return a category."""
        category = super().to_python(value)
        if category:
            category = Category.get_by_field(Category.NAME_FIELD, category,
                                             get_or_404=False)
            if not category:
                raise ValidationError(
                    _('%(value)s is not a valid category'),
                    params={'value': value},
                )
        return category


class DurationCharField(CharField):
    """ Custom CharField to return timedelta from value entered """
    # Note: don't put max_length etc. on this form field, it'll fail as
    #       timedelta doesn't have a len
    def to_python(self, value) -> timedelta:
        """Return a category."""
        duration = super().to_python(value)
        if duration:
            duration = validate_duration(duration)
        return duration


class RecipeForm(FormMixin, forms.ModelForm):
    """
    Form to update a recipe.
    """
    NAME_FF = Recipe.NAME_FIELD
    PREP_TIME_FF = Recipe.PREP_TIME_FIELD
    COOK_TIME_FF = Recipe.COOK_TIME_FIELD
    PICTURE_FF = Recipe.PICTURE_FIELD
    SERVINGS_FF = Recipe.SERVINGS_FIELD
    CATEGORY_FF = Recipe.CATEGORY_FIELD
    DESCRIPTION_FF = Recipe.DESCRIPTION_FIELD
    YIELD_FF = Recipe.RECIPE_YIELD_FIELD

    name = forms.CharField(
        label=_("Name"), max_length=Recipe.RECIPE_ATTRIB_NAME_MAX_LEN,
        required=True, widget=forms.TextInput(attrs={
            'placeholder': 'Recipe name',
        }))
    prep_time = DurationCharField(
        label=_("Prep time"), required=True, widget=forms.TextInput(attrs={
            'placeholder': f'Prep time {DURATION_FORMAT_STR}',
        }), validators=[validate_duration]
    )
    cook_time = DurationCharField(
        label=_("Cook time"), required=True, widget=forms.TextInput(attrs={
            'placeholder': f'Cook time {DURATION_FORMAT_STR}',
        }), validators=[validate_duration]
    )

    image_args = {
        "label": _("Image"),
        "required": False,
        "widget": NoCurrentClearableFileInput(attrs={
            # not all image types supported by Pillow which is used by
            # ImageField in dev mode
            "accept": ", ".join(
                DEV_IMAGE_FILE_TYPES if DEVELOPMENT else IMAGE_FILE_TYPES)
        })
    }
    # ImageField for local dev, CloudinaryFileField for production
    picture = forms.ImageField(
        **image_args
    ) if DEVELOPMENT else CloudinaryFileField(
        options={
            'folder': Recipe.picture.field.options['folder'],
        },
        **image_args
    )

    servings = forms.IntegerField(
        label=_("Servings"), min_value=1, required=True)
    category = CategoryCharField(
        required=True, widget=forms.TextInput(attrs={
            'list': 'id__category-datalist',
            'placeholder': 'Type to search...',
            'id': 'id__recipe-category-input-new'
        })
    )
    description = forms.CharField(
        label=_("Description"), max_length=Recipe.RECIPE_ATTRIB_DESC_MAX_LEN,
        required=True, widget=forms.Textarea(attrs={
            'placeholder': 'Recipe description',
        }))
    recipe_yield = forms.CharField(
        label=_("Yield"), max_length=Recipe.RECIPE_ATTRIB_YIELD_MAX_LEN,
        required=False, widget=forms.TextInput(attrs={
            'placeholder': 'Recipe yield',
        }))

    @dataclass
    class Meta:
        """ Form metadata """
        model = Recipe
        fields = [
            Recipe.NAME_FIELD, Recipe.PREP_TIME_FIELD, Recipe.COOK_TIME_FIELD,
            Recipe.PICTURE_FIELD, Recipe.SERVINGS_FIELD, Recipe.CATEGORY_FIELD,
            Recipe.DESCRIPTION_FIELD, Recipe.RECIPE_YIELD_FIELD
        ]
        non_bootstrap_fields = [Recipe.PICTURE_FIELD]
        help_texts = {
            Recipe.NAME_FIELD: 'Recipe name.',
            Recipe.PREP_TIME_FIELD: 'Recipe preparation time.',
            Recipe.COOK_TIME_FIELD: 'Recipe cook time.',
            Recipe.PICTURE_FIELD: 'Recipe picture',
            Recipe.SERVINGS_FIELD: 'Number of servings',
            Recipe.CATEGORY_FIELD: 'Recipe category',
            Recipe.DESCRIPTION_FIELD: 'Recipe description',
            Recipe.RECIPE_YIELD_FIELD: 'Recipe yield',
        }
        _error_messages = error_messages(
            model.model_name_caps(),
            ErrorMsgs(Recipe.NAME_FIELD, required=True,
                      max_length=Recipe.RECIPE_ATTRIB_NAME_MAX_LEN)
        )
        _error_messages.update(error_messages(
            model.model_name_caps(),
            *[ErrorMsgs(
                field, max_length=max_len) for field, max_len in [
                (Recipe.DESCRIPTION_FIELD, Recipe.RECIPE_ATTRIB_DESC_MAX_LEN),
                (Recipe.RECIPE_YIELD_FIELD,
                 Recipe.RECIPE_ATTRIB_YIELD_MAX_LEN),
            ]]
        ))
        _error_messages.update(error_messages(
            model.model_name_caps(),
            *[ErrorMsgs(
                field, required=True) for field in [
                    Recipe.PREP_TIME_FIELD, Recipe.COOK_TIME_FIELD,
                    Recipe.CATEGORY_FIELD
                ]]
        ))
        _error_messages.update(error_messages(
            model.model_name_caps(),
            ErrorMsgs(Recipe.SERVINGS_FIELD, required=True, min_value=1)
        ))
        error_messages = _error_messages

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # add the bootstrap class to the widget
        self.add_form_control(
            RecipeForm.Meta.fields,
            exclude=RecipeForm.Meta.non_bootstrap_fields)
