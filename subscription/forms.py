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

import ccy

from utils import FormMixin
from .models import Subscription, get_frequency_choices


def get_currency_choices() -> List[Tuple]:
    """
    Get list of currency choices
    :return:
    """
    return tuple([
        (code, ccy.currency(code).name) for code in list(ccy.all())
    ])


class SubscriptionForm(FormMixin, forms.ModelForm):
    """
    Form to create/update a Subscription.
    """

    # e.g. Decimal(10) ** -2       # same as Decimal('0.01')
    AMOUNT_EXP = Decimal(10) ** -2

    CURRENCY_CHOICES = get_currency_choices()
    FREQUENCY_CHOICES = get_frequency_choices()

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
