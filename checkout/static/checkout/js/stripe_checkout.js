/*
 * MIT License
 *
 * Copyright (c) 2023 Ian Buttimer
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to
 * deal in the Software without restriction, including without limitation the
 * rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
 * sell copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
 * FROM,OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
 * DEALINGS IN THE SOFTWARE.
 */

/**
 * Based on the sample files from https://stripe.com/docs/payments/quickstart?lang=python
 */
// This is your test publishable API key.
const stripe = Stripe(STRIPE_PUBLISHABLE_KEY);

let elements;

document
    .querySelector("#payment-form")
    .addEventListener("submit", handleSubmit);

let emailAddress = '';

// Fetches a payment intent and captures the client secret
async function initialize() {
    const response = await fetch(CREATE_PAYMENT_INTENT_URL, {
        method: "POST",
        headers: csrfHeader({
            "Content-Type": "application/json"
        }),
    });
    const { clientSecret } = await response.json();

    const appearance = {
        theme: 'stripe',
    };
    elements = stripe.elements({ appearance, clientSecret });

    const linkAuthenticationElement = elements.create("linkAuthentication");
    linkAuthenticationElement.mount("#link-authentication-element");

    linkAuthenticationElement.on('change', (event) => {
        emailAddress = event.value.email;
    });

    const paymentElementOptions = {
        layout: "tabs",
    };

    const paymentElement = elements.create("payment", paymentElementOptions);
    paymentElement.mount("#payment-element");
}

async function handleSubmit(e) {
    e.preventDefault();
    setLoading(true);

    const { error } = await stripe.confirmPayment({
        elements,
        confirmParams: {
            // Make sure to change this to your payment completion page
            return_url: stripeReturnUrl(),
            receipt_email: emailAddress,
        },
    });

    // This point will only be reached if there is an immediate error when
    // confirming the payment. Otherwise, your customer will be redirected to
    // your `return_url`. For some payment methods like iDEAL, your customer will
    // be redirected to an intermediate site first to authorize the payment, then
    // redirected to the `return_url`.
    if (error.type === "card_error" || error.type === "validation_error") {
        showMessage(error.message);
    } else {
        showMessage("An unexpected error occurred.");
    }

    setLoading(false);
}

// Fetches the payment intent status after payment submission
async function checkStatus() {
    const clientSecret = new URLSearchParams(window.location.search).get(
        "payment_intent_client_secret"
    );

    if (!clientSecret) {
        return;
    }

    const { paymentIntent } = await stripe.retrievePaymentIntent(clientSecret);

    switch (paymentIntent.status) {
        case "succeeded":
            showMessage("Payment succeeded!");
            break;
        case "processing":
            showMessage("Your payment is processing.");
            break;
        case "requires_payment_method":
            showMessage("Your payment was not successful, please try again.");
            break;
        default:
            showMessage("Something went wrong.");
            break;
    }
}

/** Set the payment currency change handler */
const setPaymentCcyChangeHandler = () => $(paymentCurrencySelectSelector).on('change', function (event) {

    $.ajax({
        url: `${UPDATE_BASKET_URL}?ccy=${event.currentTarget.value}`,
        method: 'patch',
        headers: csrfHeader()
    }).done(function(data) {
        redirectRewriteInfoResponseHandler(data);

        setBasketChangeHandler();
    });
});

/** Set the basket items change handler */
const setItemUnitsChangeHandler = () => $(basketItemUnitsSelector).on('change', function (event) {

    if (parseInt(event.currentTarget.value) < 1) {
        // warn about invalid and reset to min
        $(`#${event.currentTarget.id}`).val("1");

        showInfoToast('Minimum unit count is 1.');
    } else {
        // update basket
        $.ajax({
            url: `${event.currentTarget.attributes['data-bs-href'].value}&units=${event.currentTarget.value}`,
            method: 'patch',
            headers: csrfHeader()
        }).done(function (data) {
            redirectRewriteInfoResponseHandler(data);

            setBasketChangeHandler();
        });
    }
});

/** Set the basket change handlers */
const setBasketChangeHandler = () => {
    setPaymentCcyChangeHandler();
    setItemUnitsChangeHandler();
    setItemDeleteConfirmHandler();
    setItemDeleteHandler();
};



// ------- UI helpers -------

function showMessage(messageText) {
    const messageContainer = document.querySelector("#payment-message");

    messageContainer.classList.remove("hidden");
    messageContainer.textContent = messageText;

    setTimeout(function () {
        messageContainer.classList.add("hidden");
        messageText.textContent = "";
    }, 4000);
}

// Show a spinner on payment submission
function setLoading(isLoading) {
    if (isLoading) {
        // Disable the button and show a spinner
        document.querySelector("#id__stripe-submit").disabled = true;
        document.querySelector("#id__stripe-spinner").classList.remove("hidden");
        document.querySelector("#id__stripe-submit-button-text").classList.add("hidden");
    } else {
        document.querySelector("#id__stripe-submit").disabled = false;
        document.querySelector("#id__stripe-spinner").classList.add("hidden");
        document.querySelector("#id__stripe-submit-button-text").classList.remove("hidden");
    }
}


// payment method element
const paymentMsgNode = document.getElementById("payment-message");
// Options for the observer (which mutations to observe)
const paymentMsgConfig = { attributes: true };

// Callback function to execute when mutations are observed
const paymentMsgCallback = (mutationList, observer) => {
    for (const mutation of mutationList) {
        if (mutation.type === "attributes") {
            if (!paymentMsgNode.classList.contains("hidden")) {
                // display payment message in a toast
                showInfoToast(paymentMsgNode.innerText);
            }
        }
    }
};

// Create an observer instance linked to the callback function
const paymentMsgObserver = new MutationObserver(paymentMsgCallback);

// Start observing the target node for configured mutations
paymentMsgObserver.observe(paymentMsgNode, paymentMsgConfig);
