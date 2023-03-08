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
import json
from http import HTTPStatus
from threading import Condition, Thread
from queue import Queue
import logging

import stripe
from django.http import HttpResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

import checkout.stripe_cfg
from recipesnstuff.settings import STRIPE_WEBHOOK_KEY

import checkout.stripe_handlers as stripe_handlers


logger = logging.getLogger(__name__)

# event queue
queue = Queue()
# condition variable for notifying new events in queue
cv = Condition()


# generate handler function dictionary; handler function names take the format
# 'handler_<stripe event type>' where '.' is replaced with '_' in the event
# type, e.g. 'payment_intent.succeeded' is handled by
# 'handle_payment_intent_succeeded'. Functions are in stripe_handlers.py
HANDLERS = {
    event_type: getattr(
        stripe_handlers, f'handle_{event_type.replace(".", "_")}')
    for event_type in [
        # Stripe recommends handling
        'payment_intent.succeeded',
        'payment_intent.processing',
        'payment_intent.payment_failed',
    ]
}

# https://stripe.com/docs/payments/accept-a-payment?platform=web&ui=elements#web-test-the-integration
# for Credit card payment method
# SCENARIO: The card payment succeeds and doesn’t require authentication.
# HOW TO TEST: Fill out the credit card form using the credit card number
#              4242 4242 4242 4242 with any expiration, CVC, and postal code.
# SCENARIO: The card payment requires authentication.
# HOW TO TEST: Fill out the credit card form using the credit card number
#              4000 0025 0000 3155 with any expiration, CVC, and postal code.
# SCENARIO: The card is declined with a decline code like insufficient_funds.
# HOW TO TEST: Fill out the credit card form using the credit card number
#              4000 0000 0000 9995 with any expiration, CVC, and postal code.


@require_POST
@csrf_exempt
def stripe_webhook(request):
    """
    Stripe webhooks view.
    Based on:
    - https://stripe.com/docs/webhooks
    - https://stripe.com/docs/webhooks/quickstart?lang=python
    :param request:
    :return:
    """
    payload = request.body

    try:
        event = stripe.Event.construct_from(
            json.loads(payload), stripe.api_key
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=HTTPStatus.BAD_REQUEST)

    if STRIPE_WEBHOOK_KEY:
        # Only verify the event if there is an endpoint secret defined
        # Otherwise use the basic event deserialized with json
        sig_header = request.headers.get('stripe-signature')
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, STRIPE_WEBHOOK_KEY
            )
        except stripe.error.SignatureVerificationError as e:
            logger.warning(
                f'⚠️ Webhook signature verification failed. {str(e)}')
            return HttpResponse(status=HTTPStatus.BAD_REQUEST)
        except Exception as e:
            return HttpResponse(content=e, status=HTTPStatus.BAD_REQUEST)

    # put the event in the queue
    with cv:
        queue.put_nowait(event)
        cv.notify()

    # Send a successful 200 response to Stripe as quickly as possible because
    # Stripe retries the event if a response isn’t sent within a reasonable
    # time. Write any long-running processes as code that can run
    # asynchronously outside the webhook endpoint.
    return HttpResponse(status=HTTPStatus.OK)


def process(event_queue: Queue) -> None:
    """
    Process a Stripe event
    :param event_queue: queue to read events from
    """
    while True:
        # wait for notification there is something in queue
        with cv:
            while event_queue.qsize() == 0:
                cv.wait()
            event = event_queue.get_nowait()

        if event.type in HANDLERS:
            HANDLERS[event.type](event)
        else:
            logging.info(f'Unhandled event type {event.type}')


# start a daemon thread to process events from the queue
hook_daemon = Thread(target=process, args=(queue, ), daemon=True)
hook_daemon.start()
