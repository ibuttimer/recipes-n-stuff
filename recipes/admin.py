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

from django.contrib import admin

from .models import Category, Keyword, Measure, Ingredient


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """ Class representing the Category model in the admin interface """


@admin.register(Keyword)
class KeywordAdmin(admin.ModelAdmin):
    """ Class representing the Keyword model in the admin interface """


@admin.register(Measure)
class MeasureAdmin(admin.ModelAdmin):
    """ Class representing the Measure model in the admin interface """
    list_display = (
        Measure.NAME_FIELD,
        Measure.TYPE_FIELD,
    )


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """ Class representing the Ingredient model in the admin interface """
    list_display = (
        Ingredient.NAME_FIELD,
        Ingredient.MEASURE_FIELD,
    )
    ordering = (Ingredient.NAME_FIELD,)
