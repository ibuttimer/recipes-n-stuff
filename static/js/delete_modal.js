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
 * Set up delete modal handlers
 * @param delLinkSelector - selector for the delete entity link
 * @param delUrlSelector - selector for the var to hold the entity delete url
 * @param delConfirmModalSelector - selector for the delete confirmation modal
 * @param delBtnSelector - selector for the delete entity button
 * @param deletedModalSelector - selector for the entity deleted modal
 * @param refreshUrl - url to goto following close of entity deleted modal
 */
function setupDeleteModalHandlers (delLinkSelector, delUrlSelector, delConfirmModalSelector, delBtnSelector, deletedModalSelector, refreshUrl=undefined) {

    $(delLinkSelector).on('click', function (event) {
        /* Add delete link to delete confirm modal and display it */
        $(delUrlSelector).text(event.currentTarget.attributes['href'].textContent);

        // display confirmation modal
        $(delConfirmModalSelector).modal('show');

        event.preventDefault();
        event.stopPropagation();
    });

    $(delBtnSelector).on('click', function (event) {
        /* Delete entity and display deleted result modal */
        const url = $(delUrlSelector).text();

        $.ajax({
            method: 'delete',
            url: `${url}?ref=${window.location.pathname}`,
            headers: csrfHeader(),
        }).done(function(data) {
            const feedbackDisplayed = redirectRewriteInfoResponseHandler(data);
            if (!feedbackDisplayed) {
                // show modal
                $(deletedModalSelector).modal('show');
            }
        }).fail(function(data) {
            // display reason
            const feedbackDisplayed = redirectRewriteInfoResponseHandler(data);
            if (!feedbackDisplayed) {
                // show modal
                $(deletedModalSelector).modal('show');
            }
        });

        event.preventDefault();
        event.stopPropagation();
    });

    if (refreshUrl !== undefined) {
        $(deletedModalSelector).on('hidden.bs.modal', function (event) {
            /* refresh entity listing after deleted result modal closed */
            document.location.href = refreshUrl;
        });
    }
}
