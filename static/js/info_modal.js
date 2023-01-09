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

const infoModalIdPrefix = "id--info-modal"
const infoModalSelector = `div[id^='${infoModalIdPrefix}']`;
const infoModalTitleSelector = `h5[id^='${infoModalIdPrefix}-label']`;
const infoModalBodySelector = `div[id^='${infoModalIdPrefix}-body']`;
const infoModalOkBtnSelector = `button[id^='${infoModalIdPrefix}-ok-btn']`;
const infoModalLinkSelector = `var[id^='${infoModalIdPrefix}-url']`;

const TITLE_PROP = 'title';
const MESSAGE_PROP = 'message';
const IDENTIFIER_PROP = 'identifier';

$(document).ready(function () {

    $(infoModalSelector).on('hidden.bs.modal', function (event) {
        /* redirect on info modal close if url was provided */
        // append identifier to link selector
        const identifier = event.target.id.substring(infoModalIdPrefix.length);
        const selector = makeIdentifiedSelector(infoModalLinkSelector, "-url", identifier);
        const url = $(selector).text().trim();

        if (url.length > 0) {
            document.location.href = url;
        }
    });
});

/**
 * Make a selector for an info modal element
 * @param selector - base selector
 * @param text - text in selector to replace
 * @param identifier - text to append to `text` as replacement
 * @returns {str} - selector
 */
const makeIdentifiedSelector = (selector, text, identifier) => selector.replace(text, `${text}${identifier}`);

/**
 * Generate a selector for an info modal
 * @param identifier - modal unique identifier
 * @returns {str} - selector
 */
const modelSelector = (identifier) => makeIdentifiedSelector(infoModalSelector, infoModalIdPrefix, identifier);

/**
 * Display info modal
 * @param data - json data
 * @returns {boolean} - true if displayed
 */
function displayInfoModal(data) {
    let displayed = false;
    if (data !== undefined) {
        const identifier = `-${data[IDENTIFIER_PROP]}`;   // modal identifier
        for (const sel_prop of [
            [infoModalTitleSelector, '-label', TITLE_PROP],
            [infoModalBodySelector, '-body', MESSAGE_PROP],
            [infoModalLinkSelector, '-url', REDIRECT_PROP],
        ]) {
            const selector = makeIdentifiedSelector(sel_prop[0], sel_prop[1], identifier);
            const prop = sel_prop[2];
            let html = '';
            if (data.hasOwnProperty(prop)) {
                html = data[prop];
            }
            $(selector).html(html);
        }
        $(modelSelector(identifier)).modal('show');
        displayed = true
    }
    return displayed;
}
