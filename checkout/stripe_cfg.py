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
from datetime import datetime, timezone
import json
from typing import List

import stripe
from django.conf import settings
from django.http import HttpRequest
from stripe.api_resources.payment_intent import PaymentIntent

from django_countries import countries

from base.constants import APP_NAME_CTX
from recipesnstuff.constants import APP_NAME
from recipesnstuff.settings import STRIPE_SECRET_KEY
from subscription.models import FeatureType
from checkout.basket import Basket
from utils import dict_drill

# set Stripe API key
stripe.api_key = STRIPE_SECRET_KEY

SHIPPING_KEY = 'shipping'
METADATA_KEY = 'metadata'
ADDR_KEY = 'address'
CITY_KEY = 'city'
COUNTRY_KEY = 'country'
LINE1_KEY = 'line1'
LINE2_KEY = 'line2'
POSTCODE_KEY = 'postal_code'
STATE_KEY = 'state'
NAME_KEY = 'name'
USER_ID_KEY = 'user_id'
ADDRESS_ID_KEY = 'address_id'
ORDER_NUM_KEY = 'order_num'
WAS_1ST_X_FREE_KEY = 'was_1st_x_free'
DELIVERY_KEY = 'delivery'
DESC_KEY = 'desc'
CHARGE_KEY = 'charge'
SUBTOTAL_KEY = 'subtotal'
TOTAL_KEY = 'total'
ITEM_KEY = 'item'

ADDR_FIELDS = [
    LINE1_KEY, LINE2_KEY, CITY_KEY, STATE_KEY, POSTCODE_KEY, COUNTRY_KEY
]
COUNTRIES_DICT = dict(countries)


def generate_payment_intent_data(basket: Basket, request: HttpRequest) -> dict:
    """
    Generate the additional data to include in a Stripe payment intent
    :param basket:
    :param request:
    :return: dict of data
    """
    # https://stripe.com/docs/api/payment_intents/create#create_payment_intent-shipping
    shipping = {
        ADDR_KEY: {
            CITY_KEY: basket.address.city,
            COUNTRY_KEY: basket.address.country.code,
            LINE1_KEY: basket.address.street,
            LINE2_KEY: basket.address.street2,
            POSTCODE_KEY: basket.address.postcode,
            STATE_KEY: basket.address.state
        },
        NAME_KEY: request.user.get_full_name()
    }

    # https://stripe.com/docs/api/payment_intents/create#create_payment_intent-metadata
    # 50 keys, with key names up to 40 characters long and
    # values up to 500 characters long
    metadata = {
        USER_ID_KEY: basket.user.id,
        ADDRESS_ID_KEY: basket.address.id,
        ORDER_NUM_KEY: basket.order_num,
        WAS_1ST_X_FREE_KEY: str(
            basket.feature_type == FeatureType.FIRST_X_FREE),
        DELIVERY_KEY: json.dumps({
            DESC_KEY: basket.delivery.description,
            CHARGE_KEY: basket.format_delivery_charge_str(with_symbol=True)
        }) if basket.delivery else None,
        SUBTOTAL_KEY: basket.format_subtotal_str(with_symbol=True),
        TOTAL_KEY: basket.format_total_str(with_symbol=True),
    }
    metadata.update({
        f'{ITEM_KEY}{idx}': json.dumps(item.receipt_dict())
        for idx, item in enumerate(basket.items)
    })

    return {
        SHIPPING_KEY: shipping,
        METADATA_KEY: metadata
    }


def confirmation_context(payment_intent: PaymentIntent) -> dict:
    """
    Decode the additional data included in a Stripe payment intent
    :param payment_intent:
    :return: dict of data
    """
    shipping = payment_intent.get(SHIPPING_KEY)

    ok, metadata = dict_drill(payment_intent, METADATA_KEY)
    if ok:
        # decode elements saved as json
        ok, delivery = dict_drill(metadata, DELIVERY_KEY)
        metadata[DELIVERY_KEY] = json.loads(delivery) if ok else None

        for key, val in metadata.items():
            if key.startswith(ITEM_KEY):
                metadata[key] = json.loads(val)

    return {
        APP_NAME_CTX: APP_NAME,
        'order': {
            'full_name': shipping[NAME_KEY],
            'subtotal': metadata[SUBTOTAL_KEY],
            'delivery_desc': metadata[DELIVERY_KEY][DESC_KEY],
            'delivery_charge': metadata[DELIVERY_KEY][CHARGE_KEY],
            'total': metadata[TOTAL_KEY],
            'date': datetime.fromtimestamp(payment_intent["created"],
                                           tz=timezone.utc),
            ORDER_NUM_KEY: metadata[ORDER_NUM_KEY],
            ADDR_KEY: stripe_address_to_list(shipping[ADDR_KEY])
        },
        'contact_email': settings.DEFAULT_SEND_EMAIL
    }


def stripe_address_to_list(address: dict) -> List[str]:
    """
    Convert a Stripe address dict to a list of strings, omitting empty slots
    :param address: address dict
    :return: list of valid elements
    """
    addr = address.copy()
    code = addr[COUNTRY_KEY]
    if code in COUNTRIES_DICT:
        addr[COUNTRY_KEY] = COUNTRIES_DICT[code]

    return list(filter(
        lambda line: line is not None, [
            addr[key] if addr[key] else None for key in ADDR_FIELDS
        ]
    ))
