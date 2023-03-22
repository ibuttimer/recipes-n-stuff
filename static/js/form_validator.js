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

class ValTester {
    /**
     * Constructor
     * @param selector - element selector
     * @param testFunc - element test function
     */
    constructor(selector, testFunc) {
        this.selector = selector;
        this.testFunc = testFunc;
        this.input = undefined;
    }

    initialise() {
        this.input = document.querySelector(this.selector);
    }

    inputIsValid() {
        // https://getbootstrap.com/docs/5.2/forms/validation/
        const isValid = this.testFunc();
        let add = 'is-invalid';
        let remove = 'is-valid';

        this.input.classList.remove('is-invalid', 'is-valid');
        if (isValid) {
            add = 'is-valid';
            remove = 'is-invalid';
        }
        this.input.classList.add(add);
        this.input.classList.remove(remove);
        return isValid;
    }
}

class FormValidator {

    /**
     * Constructor
     * @param formSelector - form selector
     * @param valTesters - list of testers
     * @param onSubmitFail - optional function to execute when form submit tests fail
     */
    constructor(formSelector, valTesters, onSubmitFail = undefined) {
        this.formSelector = formSelector;
        this.valTesters = valTesters;
        this.onSubmitFail = onSubmitFail;

        this.form = undefined;      // form element
    }

    /** Initialise the validator */
    initialise() {
        this.form = document.querySelector(this.formSelector);

        for (const tester of this.valTesters) {
            tester.initialise();

            tester.input.addEventListener('change', (event) => {
                // handle input change
                tester.inputIsValid();
            });
            tester.input.addEventListener('input', function (event) {
                // remove classes on any new input keypress
                event.currentTarget.classList.remove('is-invalid', 'is-valid', 'was-validated', 'valid');
            });
        }
        this.form.addEventListener('submit', (event) => {
            if (!this.inputIsValid()) {
                event.preventDefault();

                if (this.onSubmitFail !== undefined && this.onSubmitFail !== null) {
                    this.onSubmitFail(event);
                }
            }
        });
    }

    /**
     * Validate that the new input is valid
     *
     * TODO custom validation edge cases require more work
     *
     * @param event - event, may be 'change' or 'submit'
     * @returns {boolean}
     */
    inputIsValid() {
        let isValid = true;
        for (const tester of this.valTesters) {
            if (!tester.inputIsValid()) {
                isValid = false;
            }
        }
        return isValid;
    }
}