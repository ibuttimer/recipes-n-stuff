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

const {getByTestId, screen} = require('@testing-library/dom');
require('@testing-library/jest-dom');
require('@testing-library/jest-dom/extend-expect');
require('@testing-library/jest-dom/matchers');
const path = require('path');

const appName = "Recipes 'N' Stuff";

const timeout = 10000;
const usernameSelector = '#id_login';
const passwordSelector = '#id_password';
const registerSelector = '[id^=id--register]';
const signInSelector = '[id^=id--sign-in]';
const signOutSelector = '#id--sign-out';
const reactionsSelectedClass = "reactions-selected";

describe(
    'Login Page',
    () => {
        let page;
        beforeAll(async () => {
            page = await globalThis.__BROWSER_GLOBAL__.newPage();
            await page.goto(globalThis.HOST_URL);
        }, timeout);

        it(`Landing should be titled "${appName}"`, async () => {
            await expect(page.title()).resolves.toMatch(appName);
        });

        it('Landing should load without error', async () => {
            let element = await page.$(signInSelector);
            await expect((await element.getProperty("innerText")).jsonValue()).resolves.toMatch('Sign In');
            await element.dispose();

            element = await page.$(registerSelector);
            await expect((await element.getProperty("innerText")).jsonValue()).resolves.toMatch('Register');
            await element.dispose();
        });

        it('Sign In should be titled "Sign In"', async () => {
            const url = path.join(globalThis.HOST_URL, '/accounts/login/');
            await page.goto(url);
            await expect(page.title()).resolves.toMatch('Sign In');
        }, timeout);

        it('Sign In should login', async () => {
            for (const selector of [
                usernameSelector, passwordSelector, signInSelector
            ]) {
                const element = await page.$(selector);
                await expect(element !== null).toBeTruthy();
                await element.dispose();
            }

            // https://devdocs.io/puppeteer/index#pagetypeselector-text-options
            await page.type(usernameSelector, globalThis.USERNAME, {delay: 100}); // Types slower, like a user
            await page.type(passwordSelector, globalThis.PASSWORD, {delay: 100}); // Types slower, like a user

            // https://devdocs.io/puppeteer/index#pageclickselector-options
            // need to wait for click & navigation together to avoid possible race condition
            await Promise.all([
                page.waitForNavigation({timeout: timeout}),
                page.click(signInSelector),
            ]);

            const bodyHandle = await page.$('body');
            await expect(page.evaluate(body => body.innerHTML, bodyHandle)).resolves.toMatch(`Successfully signed in as ${globalThis.USERNAME}`);
            await bodyHandle.dispose();
        }, timeout);

        it('should logout', async () => {
            const url = path.join(globalThis.HOST_URL, '/accounts/logout/');

            await page.goto(url);

            // https://devdocs.io/puppeteer/index#pageclickselector-options
            // need to wait for click & navigation together to avoid possible race condition
            await Promise.all([
                page.waitForNavigation({timeout: timeout}),
                page.click(signOutSelector),
            ]);

            const bodyHandle = await page.$('body');
            await expect(page.evaluate(body => body.innerHTML, bodyHandle)).resolves.toMatch(`You have signed out`);
            await bodyHandle.dispose();

        }, timeout);
    },
    timeout,
);
