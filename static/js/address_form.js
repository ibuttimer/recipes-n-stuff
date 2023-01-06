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
 *
 */

// Add address card is named 'id--address-new'
const COUNTRY_SELECT_SELECTOR = "#id_country";

/* Click handler for new address */
function countrySelectedClickHandler(event) {
    if (event.target.value.length > 0) {
        $.ajax({
            method: 'get',
            url: SUBDIVISION_URL.replace(COUNTRY_CODE, event.target.value),
        }).done(function (data) {
            redirect_rewrite_response_handler(data)
        });
    }
}

/* Add handlers to request more comments */
function addCountrySelectedHandler() {
    /* Click handler to request more comments */
    $(COUNTRY_SELECT_SELECTOR).on('change', countrySelectedClickHandler);
}

$(document).ready(function () {
    /* Handler for new address */
    addCountrySelectedHandler();
});
