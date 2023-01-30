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

# name of this app
THIS_APP = Path(__file__).resolve().parent.name

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
DATE_PUBLISHED_FIELD = 'date_published'
DESCRIPTION_FIELD = 'description'
CATEGORY_FIELD = 'category'
KEYWORDS_FIELD = 'keywords'
AUTHOR_FIELD = 'author'
SERVINGS_FIELD = 'servings'
RECIPE_YIELD_FIELD = 'recipe_yield'
INGREDIENTS_FIELD = 'ingredients'
INSTRUCTIONS_FIELD = 'instructions'
