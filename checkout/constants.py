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

from utils import append_slash

# name of this app
THIS_APP = Path(__file__).resolve().parent.name

# models related
CURRENCY_CODE_MAX_LEN: int = 3
CURRENCY_CODE_FIELD = 'code'
NUMERIC_CODE_FIELD = 'numeric_code'
DIGITS_CODE_FIELD = 'digits'
NAME_FIELD = 'name'
TIMESTAMP_FIELD = 'timestamp'
BASE_FIELD = 'base'
RATES_FIELD = 'rates'

# urls/routes related
CHECKOUT_PAY_URL = append_slash("pay")
CHECKOUT_CREATE_PAYMENT_URL = append_slash("payment-intent")
CHECKOUT_UPDATE_BASKET_URL = append_slash("update-basket")
CHECKOUT_PAID_URL = append_slash("paid")

CHECKOUT_PAY_ROUTE_NAME = "pay"
CHECKOUT_CREATE_PAYMENT_ROUTE_NAME = "payment_intent"
CHECKOUT_UPDATE_BASKET_ROUTE_NAME = "update_basket"
CHECKOUT_PAID_ROUTE_NAME = "paid"

# query related
BASKET_CCY_QUERY = 'ccy'
ITEM_QUERY = 'item'
UNITS_QUERY = 'units'


# context related
STRIPE_PUBLISHABLE_KEY_CTX = 'stripe_publishable_key'
STRIPE_RETURN_URL_CTX = 'stripe_return_url'
BASKET_CTX = 'basket'
CURRENCIES_CTX = 'currencies'

# session related
BASKET_SES = 'basket'


# zero decimal currencies; https://stripe.com/docs/currencies#zero-decimal
ZERO_DECIMAL_CURRENCIES = [
    'BIF', 'CLP', 'DJF', 'GNF', 'JPY', 'KMF', 'KRW', 'MGA', 'PYG', 'RWF',
    'UGX', 'VND', 'VUV', 'XAF', 'XOF', 'XPF'
]
# The Malagasy ariary are technically divided into five subunits, but these
# are not used in practice, hence Stripe treats it as a zero-decimal
# currency.

# three decimal currencies; https://stripe.com/docs/currencies#three-decimal
# must round amounts to the nearest ten. E.g., 5.124 KWD must be rounded to
# 5120 or 5130
THREE_DECIMAL_CURRENCIES = [
    'BHD', 'JOD', 'KWD', 'OMR', 'TND'
]
