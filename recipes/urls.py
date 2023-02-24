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
#

from django.urls import path

from .constants import (
    THIS_APP, RECIPES_URL, RECIPES_ROUTE_NAME,
    RECIPE_SEARCH_URL, RECIPE_SEARCH_ROUTE_NAME,
    RECIPE_NEW_URL, RECIPE_NEW_ROUTE_NAME,
    RECIPE_ID_URL, RECIPE_ID_ROUTE_NAME,
    RECIPE_ID_UPDATE_URL, RECIPE_ID_UPDATE_ROUTE_NAME,
    RECIPE_INGREDIENT_ID_URL, RECIPE_INGREDIENTS_ROUTE_NAME,
    RECIPE_INGREDIENT_ID_ROUTE_NAME, RECIPE_ID_INGREDIENT_NEW_URL,
    RECIPE_ID_INGREDIENT_NEW_ROUTE_NAME,
    RECIPE_INSTRUCTION_ID_ROUTE_NAME, RECIPE_ID_INSTRUCTION_NEW_URL,
    RECIPE_ID_INSTRUCTION_NEW_ROUTE_NAME, RECIPE_INSTRUCTION_ID_URL,
    RECIPE_ID_BUY_BOX_ROUTE_NAME, RECIPE_ID_BUY_BOX_URL
)
from .views import (
    # RecipeCreate,
    RecipeList, SearchRecipeList,
    RecipeDetail, RecipeDetailUpdate, add_recipe_to_basket,
    RecipeIngredientDetail, create_recipe_ingredient,
    InstructionDetail, create_recipe_instruction,
)

# https://docs.djangoproject.com/en/4.1/topics/http/urls/#url-namespaces-and-included-urlconfs
app_name = THIS_APP

urlpatterns = [
    path(RECIPES_URL, RecipeList.as_view(), name=RECIPES_ROUTE_NAME),
    path(RECIPE_SEARCH_URL, SearchRecipeList.as_view(),
         name=RECIPE_SEARCH_ROUTE_NAME),
    # path(RECIPE_NEW_URL, AddressCreate.as_view(),
    #      name=RECIPE_NEW_ROUTE_NAME),
    path(RECIPE_ID_URL, RecipeDetail.as_view(), name=RECIPE_ID_ROUTE_NAME),
    path(RECIPE_ID_UPDATE_URL, RecipeDetailUpdate.as_view(),
         name=RECIPE_ID_UPDATE_ROUTE_NAME),
    path(RECIPE_ID_BUY_BOX_URL, add_recipe_to_basket,
         name=RECIPE_ID_BUY_BOX_ROUTE_NAME),

    path(RECIPE_INGREDIENT_ID_URL, RecipeIngredientDetail.as_view(),
         name=RECIPE_INGREDIENT_ID_ROUTE_NAME),
    path(RECIPE_ID_INGREDIENT_NEW_URL, create_recipe_ingredient,
         name=RECIPE_ID_INGREDIENT_NEW_ROUTE_NAME),

    path(RECIPE_INSTRUCTION_ID_URL, InstructionDetail.as_view(),
         name=RECIPE_INSTRUCTION_ID_ROUTE_NAME),
    path(RECIPE_ID_INSTRUCTION_NEW_URL, create_recipe_instruction,
         name=RECIPE_ID_INSTRUCTION_NEW_ROUTE_NAME),
]
