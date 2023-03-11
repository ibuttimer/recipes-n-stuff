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
from pathlib import Path

from utils import url_path

# name of this app
THIS_APP = Path(__file__).resolve().parent.name

# common field names
NAME_FIELD = "name"
TYPE_FIELD = "type"
SYSTEM_FIELD = "system"
IS_DEFAULT_FIELD = "is_default"
ABBREV_FIELD = 'abbrev'
BASE_US_FIELD = 'base_us'
BASE_METRIC_FIELD = 'base_metric'
MEASURE_FIELD = 'measure'

FOOD_ID_FIELD = "food_id"

TEXT_FIELD = 'text'

URL_FIELD = 'url'
RECIPE_FIELD = 'recipe'

PREP_TIME_FIELD = 'prep_time'
COOK_TIME_FIELD = 'cook_time'
TOTAL_TIME_FIELD = 'total_time'
DATE_PUBLISHED_FIELD = 'date_published'
DESCRIPTION_FIELD = 'description'
CATEGORY_FIELD = 'category'
KEYWORDS_FIELD = 'keywords'
AUTHOR_FIELD = 'author'
SERVINGS_FIELD = 'servings'
RECIPE_YIELD_FIELD = 'recipe_yield'
INGREDIENTS_FIELD = 'ingredients'
INSTRUCTIONS_FIELD = 'instructions'
IMAGES_FIELD = 'images'
CALORIES_FIELD = 'calories'
FAT_CONTENT_FIELD = 'fat_content'
SATURATED_FAT_CONTENT_FIELD = 'saturated_fat_content'
CHOLESTEROL_CONTENT_FIELD = 'cholesterol_content'
SODIUM_CONTENT_FIELD = 'sodium_content'
CARBOHYDRATE_CONTENT_FIELD = 'carbohydrate_content'
FIBRE_CONTENT_FIELD = 'fibre_content'
SUGAR_CONTENT_FIELD = 'sugar_content'
PROTEIN_CONTENT_FIELD = 'protein_content'

INGREDIENT_FIELD = 'ingredient'
QUANTITY_FIELD = 'quantity'
INDEX_FIELD = 'index'

# Recipe routes related
PK_PARAM_NAME = "pk"
INGREDIENT_PK_PARAM_NAME = "ingredient_pk"
RECIPES_URL = ""
RECIPE_SEARCH_URL = url_path(RECIPES_URL, "search")
RECIPE_NEW_URL = url_path(RECIPES_URL, "new")
RECIPE_ID_URL = url_path(RECIPES_URL, f"<int:{PK_PARAM_NAME}>")
RECIPE_ID_UPDATE_URL = url_path(RECIPE_ID_URL, "update")
RECIPE_ID_BUY_BOX_URL = url_path(RECIPE_ID_URL, "buy_box")
RECIPE_ID_INGREDIENT_NEW_URL = url_path(RECIPE_ID_URL, "ingredient", "new")
RECIPE_ID_INSTRUCTION_NEW_URL = url_path(RECIPE_ID_URL, "instruction", "new")

RECIPE_INGREDIENTS_URL = "ingredients"
RECIPE_INGREDIENT_ID_URL = \
    url_path(RECIPE_INGREDIENTS_URL, f"<int:{PK_PARAM_NAME}>")
RECIPE_INSTRUCTIONS_URL = "instructions"
RECIPE_INSTRUCTION_ID_URL = \
    url_path(RECIPE_INSTRUCTIONS_URL, f"<int:{PK_PARAM_NAME}>")

LETTER_PARAM_NAME = "letter"
RECIPE_CATEGORIES_URL = url_path(RECIPES_URL, "categories")

# convention is recipes route names begin with 'recipe'
RECIPES_ROUTE_NAME = "recipes"
RECIPE_SEARCH_ROUTE_NAME = "recipe_search"
RECIPE_NEW_ROUTE_NAME = "recipe_new"
RECIPE_ID_ROUTE_NAME = "recipe_id"
RECIPE_ID_UPDATE_ROUTE_NAME = "recipe_id_update"
RECIPE_ID_BUY_BOX_ROUTE_NAME = "recipe_id_buy_box"
RECIPE_ID_INGREDIENT_NEW_ROUTE_NAME = "recipe_id_ingredient_new"
RECIPE_ID_INSTRUCTION_NEW_ROUTE_NAME = "recipe_id_instruction_new"

RECIPE_INGREDIENTS_ROUTE_NAME = "recipe_ingredients"
RECIPE_INGREDIENT_ID_ROUTE_NAME = "recipe_ingredient_id"
RECIPE_INSTRUCTIONS_ROUTE_NAME = "recipe_instructions"
RECIPE_INSTRUCTION_ID_ROUTE_NAME = "recipe_instruction_id"

CATEGORIES_ROUTE_NAME = "recipe_categories"

# query related
NEXT_QUERY = 'next'
LETTER_QUERY = 'letter'
CATEGORY_QUERY = 'category'

# context related
RECIPE_FORM_CTX = 'recipe_form'
RECIPE_LIST_CTX = 'recipe_list'
RECIPE_DTO_CTX = 'recipe_dto'
INGREDIENTS_CTX = 'ingredients'
NEW_INGREDIENT_FORM_CTX = 'new_ingred_form'
INGREDIENT_LIST_CTX = 'ingredient_list'
INSTRUCTIONS_CTX = 'instructions'
NEW_INSTRUCTION_FORM_CTX = 'new_instruct_form'
NEW_URL_CTX = 'new_url'
REFRESH_URL_CTX = 'refresh_url'
KEYWORDS_CTX = 'keywords'
TIME_CTX = 'time'
CATEGORY_LIST_CTX = 'category_list'
LETTERS_CTX = 'letters'
LETTER_CTX = 'letter'
CATEGORY_CTX = 'category'
AUTHOR_CTX = 'author'
RECIPE_COUNT_CTX = 'recipe_count'

COUNT_OPTIONS_CTX = 'count_options'
SELECTED_COUNT_CTX = 'selected_count'
CUSTOM_COUNT_CTX = 'custom_count'
CCY_SYMBOL_CTX = 'ccy_symbol'
UNIT_PRICE_CTX = 'unit_price'
SKU_CTX = 'sku'

# query related
INGREDIENTS_QUERY = 'ingredients'
INSTRUCTIONS_QUERY = 'instructions'
AUTHOR_QUERY = 'author'
KEYWORD_QUERY = 'key'              # keyword
INGREDIENT_QUERY = 'ingredient'
