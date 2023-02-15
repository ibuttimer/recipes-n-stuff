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
 * Toggle the icon and spinner display for the specified selector
 * @param selector
 */
function hideIconShowSpinner(selector) {
    /* hide upload icon and show in progress spinner */
    $(`${selector} > i`).attr("hidden", "hidden");
    $(`${selector} > span`).removeAttr("hidden");
}

/**
 * Toggle the icon and spinner display for the specified selector
 * @param selector
 */
function showIconHideSpinner(selector) {
    /* hide upload icon and show in progress spinner */
    $(`${selector} > i`).removeAttr("hidden");
    $(`${selector} > span`).attr("hidden", "hidden");
}

/**
 * Toggle the icon and spinner display for the specified selector
 * @param selector
 */
function toggleIconAndSpinner(selector) {
    /* hide/show upload icon and show/hide in progress spinner */
    const hidden = $(`${selector} > i`).attr("hidden");
    if (!hidden) {
        hideIconShowSpinner(selector);
    } else {
        showIconHideSpinner(selector);
    }
}

/**
 * Set up the handlers for instruction/ingredient add/update/delete
 * @param newSelector - add new button selector
 * @param updateSelector - update button selector
 * @param delSelector - delete button selector
 * @param delCloseSelector - delete modal close button selector
 * @param delCancelSelector - delete modal cancel button selector
 */
function setupAddUpdateDelHandlers(newSelector, updateSelector, delSelector, delCloseSelector, delCancelSelector) {

    $(newSelector).on('click', function (event) {
        /* hide upload icon and display in progress spinner */
        hideIconShowSpinner(newSelector);
    });

    for (const selector of [updateSelector, delSelector]) {
        $(selector).on('click', function (event) {
            /* hide upload icon and display in progress spinner */
            toggleIconAndSpinner(`#${event.currentTarget.id}`);
        });
    }

    for (const selector of [delCloseSelector, delCancelSelector]) {
        $(selector).on('click', function (event) {
            /* show upload icon and hide in progress spinner */
            showIconHideSpinner(delSelector);
        });
    }

    // Fetch all the forms we want to apply custom Bootstrap validation styles to
    const forms = document.querySelectorAll('.needs-validation')

    // Loop over them and prevent submission
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();

                showIconHideSpinner(newSelector);
                showIconHideSpinner(updateSelector);
            }

            form.classList.add('was-validated')
        }, false);
    })
}
