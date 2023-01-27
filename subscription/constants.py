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

NAME_FIELD = "name"
FREQUENCY_FIELD = "frequency"
FREQUENCY_TYPE_FIELD = "frequency_type"
FEATURE_TYPE_FIELD = "feature_type"
AMOUNT_FIELD = "amount"
BASE_CURRENCY_FIELD = "base_currency"
DESCRIPTION_FIELD = "description"
CALL_TO_PICK_FIELD = "call_to_pick"
FEATURES_FIELD = "features"
COUNT_FIELD = "count"
IS_ACTIVE_FIELD = "is_active"

USER_FIELD = "user"
SUBSCRIPTION_FIELD = "subscription"
START_DATE_FIELD = "start_date"
END_DATE_FIELD = "end_date"

# urls/routes related
SUBSCRIPTIONS_URL = ""
SUBSCRIPTION_NEW_URL = append_slash("new")
SUBSCRIPTION_BY_ID_URL = append_slash("<int:pk>")
SUBSCRIPTION_CHOICE_URL = append_slash("choice")
SUBSCRIPTION_PICK_URL = url_path("pick", "<int:pk>")

SUBSCRIPTIONS_ROUTE_NAME = "subscriptions"
SUBSCRIPTION_NEW_ROUTE_NAME = "subscription_new"
SUBSCRIPTION_ID_ROUTE_NAME = "subscription_id"
SUBSCRIPTION_CHOICE_ROUTE_NAME = "subscription_choice"
SUBSCRIPTION_PICK_ROUTE_NAME = "subscription_pick"

# context related
SUBSCRIPTION_FORM_CTX = 'subscription_form'
SUBSCRIPTION_LIST_CTX = 'subscription_list'

# query related
IS_ACTIVE_QUERY: str = 'active'
