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
from dataclasses import dataclass
from typing import Tuple

from django.utils.translation import gettext_lazy as _

from django import forms

from checkout.currency import get_currencies
from recipesnstuff.settings import DEFAULT_CURRENCY, PRICING_FACTOR
from utils import FormMixin
from .mixin import QuantiseMixin
from .models import Subscription, FrequencyType


# https://en.wikipedia.org/wiki/G10_currencies
G10_CURRENCIES = sorted([
    'AUD', 'CAD', 'EUR', 'JPY', 'NZD', 'NOK', 'GBP', 'SEK', 'CHF', 'USD'
])


def get_currency_choices() -> Tuple[Tuple[str, str]]:
    """
    Get list of currency choices
    :return: list of tuples of currency code and name
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


class SubscriptionForm(FormMixin, QuantiseMixin, forms.ModelForm):
    """
    Form to create/update a Subscription.
    """
    # field names
    NAME_FF = Subscription.NAME_FIELD
    FREQUENCY_TYPE_FF = Subscription.FREQUENCY_TYPE_FIELD
    FREQUENCY_FF = Subscription.FREQUENCY_FIELD
    AMOUNT_FF = Subscription.AMOUNT_FIELD
    BASE_CURRENCY_FF = Subscription.BASE_CURRENCY_FIELD
    DESCRIPTION_FF = Subscription.DESCRIPTION_FIELD
    CALL_TO_PICK_FF = Subscription.CALL_TO_PICK_FIELD
    FEATURES_FF = Subscription.FEATURES_FIELD
    IS_ACTIVE_FF = Subscription.IS_ACTIVE_FIELD

    CURRENCY_CHOICES = None
    FREQUENCY_CHOICES = FrequencyType.get_frequency_choices()

    name = forms.CharField(
        label=_("Name"),
        max_length=Subscription.SUBSCRIPTION_ATTRIB_NAME_MAX_LEN,
        required=True)

    frequency_type = forms.ChoiceField(
        label=_("Frequency type"), required=True, choices=FREQUENCY_CHOICES)

    frequency = forms.IntegerField(label=_("Frequency"))

    amount = forms.DecimalField(decimal_places=PRICING_FACTOR)

    # choices set during init
    base_currency = forms.ChoiceField(
        label=_("Base currency"), required=True, choices=())

    description = forms.CharField(
        label=_("Description"),
        max_length=Subscription.SUBSCRIPTION_ATTRIB_DESCRIPTION_MAX_LEN,
        required=True)

    call_to_pick = forms.CharField(
        label=_("Call to pick"),
        max_length=Subscription.SUBSCRIPTION_ATTRIB_CALL_TO_PICK_MAX_LEN,
        required=True)

    is_active = forms.BooleanField(
        label=_("Is active"), initial=True, required=False)

    @dataclass
    class Meta:
        """ Model metadata """
        model = Subscription
        fields = [
            Subscription.NAME_FIELD, Subscription.DESCRIPTION_FIELD,
            Subscription.FREQUENCY_TYPE_FIELD, Subscription.FREQUENCY_FIELD,
            Subscription.BASE_CURRENCY_FIELD, Subscription.AMOUNT_FIELD,
            Subscription.CALL_TO_PICK_FIELD, Subscription.IS_ACTIVE_FIELD
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

        self.fields[self.BASE_CURRENCY_FF].choices = self.currency_choices

    @property
    def currency_choices(self):
        """ Currency choices """
        # lazy loading and caching of currency choices as it hits the database
        if self.CURRENCY_CHOICES is None:
            self.CURRENCY_CHOICES = get_currency_choices()
        return self.CURRENCY_CHOICES
