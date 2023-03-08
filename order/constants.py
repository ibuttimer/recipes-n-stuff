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
from utils import append_slash, url_path

# name of this app
THIS_APP = Path(__file__).resolve().parent.name

# common field names
USER_FIELD = 'user'
CREATED_FIELD = 'created'
UPDATED_FIELD = 'updated'
STATUS_FIELD = 'status'
AMOUNT_FIELD = 'amount'
BASE_CURRENCY_FIELD = 'base_currency'
AMOUNT_BASE_FIELD = 'amount_base'
ORDER_NUM_FIELD = 'order_num'
ITEMS_FIELD = 'items'
WAS_1ST_X_FREE_FIELD = 'was_1st_x_free'
INFO_FIELD = 'info'
TYPE_FIELD = 'type'
SUBSCRIPTION_FIELD = 'subscription'
RECIPE_FIELD = 'recipe'
COUNTRY_FIELD = 'country'
UNIT_PRICE_FIELD = 'unit_price'
SKU_FIELD = 'sku'
DESCRIPTION_FIELD = 'description'

# context related
