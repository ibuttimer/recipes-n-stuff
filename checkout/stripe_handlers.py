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
import logging
from typing import Optional, Tuple

from stripe.api_resources.payment_intent import PaymentIntent
from stripe.stripe_object import StripeObject

from base import send_email, EmailOpt
from checkout.constants import THIS_APP
from checkout.stripe_cfg import confirmation_context
from order.models import OrderStatus
from order.persist import update_order_status
from utils import dict_drill, app_template_path

logger = logging.getLogger(__name__)

# PaymentIntent object
# https://stripe.com/docs/api/payment_intents/object?lang=python


def get_order_num(
        event: StripeObject) -> Tuple[Optional[str], PaymentIntent]:
    """
    Get order number from a payment intent event metadata.
    :param event: Stripe event
    :return order num or None
    """
    payment_intent = event.data.object  # contains a stripe.PaymentIntent

    ok, order_num = dict_drill(payment_intent, 'metadata', 'order_num')
    if not ok:
        logger.warning(f'Handling {event.type}: order number not found')
        order_num = None

    return order_num, payment_intent


def handle_payment_intent_succeeded(event: StripeObject):
    """
    Handle 'payment_intent.succeeded' event.
    Occurs when a PaymentIntent has successfully completed payment.
    https://stripe.com/docs/api/events/types?lang=python#event_types-payment_intent.succeeded
    data.object is a payment intent
    :param event: Stripe event
    """
    order_num, payment_intent = get_order_num(event)
    if order_num:
        update_order_status(order_num, OrderStatus.PAID)

        # send confirmation email
        send_email(
            app_template_path(
                THIS_APP, 'email', 'confirmation_email_subject.txt'),
            app_template_path(
                THIS_APP, 'email', 'confirmation_email_body.txt'),
            payment_intent['receipt_email'],
            opt=EmailOpt.ALL_TEMPLATE,
            context=confirmation_context(payment_intent)
        )

    logger.debug(f'Handled {event.type}')


def handle_payment_intent_processing(event: StripeObject):
    """
    Handle 'payment_intent.processing' event.
    Occurs when a PaymentIntent has started processing.
    https://stripe.com/docs/api/events/types?lang=python#event_types-payment_intent.processing
    data.object is a payment intent
    :param event: Stripe event
    """
    order_num, _ = get_order_num(event)
    if order_num:
        update_order_status(order_num, OrderStatus.PROCESSING_PAYMENT)

    logger.debug(f'Handled {event.type}')


def handle_payment_intent_payment_failed(event: StripeObject):
    """
    Handle 'payment_intent.processing' event.
    Occurs when a PaymentIntent has failed the attempt to create a payment
    method or a payment.
    https://stripe.com/docs/api/events/types?lang=python#event_types-payment_intent.payment_failed
    data.object is a payment intent
    :param event: Stripe event
    """
    order_num, _ = get_order_num(event)
    if order_num:
        payment_intent = event.data.object  # contains a stripe.PaymentIntent
        # get reason
        cok, code = dict_drill(payment_intent, 'last_payment_error', 'code')
        dok, decline_code = dict_drill(payment_intent, 'last_payment_error',
                                       'decline_code')
        info = f'{code if cok else ""} {decline_code if dok else ""}'
        if info.isspace():
            info = None

        update_order_status(order_num, OrderStatus.PAYMENT_FAILED, info=info)

    logger.info(f'Handled {event.type}')
