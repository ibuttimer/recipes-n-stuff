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

from decimal import Decimal
from typing import List, Tuple

from django.utils.translation import gettext_lazy as _

from django import forms

from checkout.currency import get_currencies
from recipesnstuff.settings import DEFAULT_CURRENCY
from utils import FormMixin
from .models import Subscription, FrequencyType


# https://en.wikipedia.org/wiki/G10_currencies
G10_CURRENCIES = sorted([
    'AUD', 'CAD', 'EUR', 'JPY', 'NZD', 'NOK', 'GBP', 'SEK', 'CHF', 'USD'
])


def get_currency_choices() -> Tuple[Tuple[str, str]]:
    """
    Get list of currency choices
    :return:
    """
    currencies = get_currencies()
    default = DEFAULT_CURRENCY.upper()

    def choice(code: str) -> tuple:
        code = code.upper()
        return currencies[code].code, currencies[code].name

    def add_choice(code: str) -> bool:
        return code in currencies and code != default

    # add default currency
    choices = [
        choice(default)
    ] if default in currencies else []
    # add g10 currencies
    choices.extend([
        choice(code) for code in G10_CURRENCIES if add_choice(code)
    ])
    # add remaining currencies
    non_g10 = sorted([
        code for code in currencies.keys() if code not in G10_CURRENCIES
    ])
    choices.extend([
        choice(code) for code in non_g10 if add_choice(code)
    ])
    return tuple(choices)


class SubscriptionForm(FormMixin, forms.ModelForm):
    """
    Form to create/update a Subscription.
    """

    # e.g. Decimal(10) ** -2       # same as Decimal('0.01')
    AMOUNT_EXP = Decimal(10) ** -2

    CURRENCY_CHOICES = get_currency_choices()
    FREQUENCY_CHOICES = FrequencyType.get_frequency_choices()

    name = forms.CharField(
        label=_("Name"),
        max_length=Subscription.SUBSCRIPTION_ATTRIB_NAME_MAX_LEN,
        required=True)

    frequency_type = forms.ChoiceField(
        label=_("Frequency type"), required=True, choices=FREQUENCY_CHOICES)

    frequency = forms.IntegerField(label=_("Frequency"))

    amount = forms.DecimalField(decimal_places=2)

    base_currency = forms.ChoiceField(
        label=_("Base currency"), required=True, choices=CURRENCY_CHOICES)

    description = forms.CharField(
        label=_("Description"),
        max_length=Subscription.SUBSCRIPTION_ATTRIB_DESCRIPTION_MAX_LEN,
        required=True)

    is_active = forms.BooleanField(label=_("Is active"), initial=True)

    class Meta:
        model = Subscription
        fields = [
            Subscription.NAME_FIELD, Subscription.DESCRIPTION_FIELD,
            Subscription.FREQUENCY_TYPE_FIELD, Subscription.FREQUENCY_FIELD,
            Subscription.BASE_CURRENCY_FIELD, Subscription.AMOUNT_FIELD,
            Subscription.IS_ACTIVE_FIELD
        ]
        bool_fields = [
            Subscription.IS_ACTIVE_FIELD
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # add the bootstrap class to the widget
        self.add_form_control(SubscriptionForm.Meta.fields,
                              exclude=SubscriptionForm.Meta.bool_fields)
        self.add_form_check_input(SubscriptionForm.Meta.bool_fields)

    @staticmethod
    def quantise_amount(amount: Decimal):
        return amount.quantize(SubscriptionForm.AMOUNT_EXP)
