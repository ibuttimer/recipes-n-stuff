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

#  MIT License
#
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to
#  deal in the Software without restriction, including without limitation the
#  rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
#  sell copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#
#
from django.test import TestCase

from recipes.models import (
    Category, Keyword, Ingredient, Instruction, Recipe, RecipeIngredient,
    Image, Measure
)


class TestCategoryModel(TestCase):
    """
    Test Category model
    https://docs.djangoproject.com/en/4.1/topics/testing/tools/
    """

    def test_category_defaults(self):
        """ Test Category model defaults """
        instance = Category.objects.create()
        self.assertIsNotNone(instance)
        for field in [
            Category.NAME_FIELD
        ]:
            with self.subTest(field=field):
                self.assertEqual(instance.get_field(field), '')


class TestKeywordModel(TestCase):
    """
    Test Keyword model
    https://docs.djangoproject.com/en/4.1/topics/testing/tools/
    """

    def test_category_defaults(self):
        """ Test Keyword model defaults """
        instance = Keyword.objects.create()
        self.assertIsNotNone(instance)
        for field in [
            Keyword.NAME_FIELD
        ]:
            with self.subTest(field=field):
                self.assertEqual(instance.get_field(field), '')


class TestIngredientModel(TestCase):
    """
    Test Ingredient model
    https://docs.djangoproject.com/en/4.1/topics/testing/tools/
    """

    def test_category_defaults(self):
        """ Test Ingredient model defaults """
        fixtures = ['measure.json']

        default_unit = Measure.get_default_unit()

        instance = Ingredient.objects.create(**{
            f'{Ingredient.MEASURE_FIELD}': default_unit
        })
        self.assertIsNotNone(instance)
        for field in [
            Ingredient.NAME_FIELD
        ]:
            with self.subTest(field=field):
                self.assertEqual(instance.get_field(field), '')


class TestInstructionModel(TestCase):
    """
    Test Instruction model
    https://docs.djangoproject.com/en/4.1/topics/testing/tools/
    """

    def test_category_defaults(self):
        """ Test Instruction model defaults """
        instance = Instruction.objects.create()
        self.assertIsNotNone(instance)
        for field in [
            Instruction.TEXT_FIELD
        ]:
            with self.subTest(field=field):
                self.assertEqual(instance.get_field(field), '')


# TODO generate fixtures to test Recipe, RecipeIngredient, Image
