/*
 * MIT License
 *
 * Copyright (c) 2022-2023 Ian Buttimer
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

/**
 * Node.js script of view configurations for 'lighthouse.js' and 'scrape.js'.
 */

export const loginUrl = '/accounts/login/';
export const logoutUrl = '/accounts/logout/';

/**
 * View config
 * @param {string} name - report name
 * @param {boolean} login - login required flag; true = needs to be logged in, false = does not need to be logged in
 * @param {string} path - relative path to generated file
 * @param {string} desc - description
 * @returns
 */
const viewCfg = (name, login, path, desc) => {
    return { name: name, login: login, path: path, desc: desc };
};
const validatorPath = 'val-test'
export const landingView = 'landing';
export const loginView = 'login';
export const signupView = 'signup';
export const socialLoginView = 'social-login';
export const logoutView = 'logout';
export const logoutValTestView = `${logoutView}-${validatorPath}`;
export const homeView = 'home';
export const homeValTest = `${homeView}-${validatorPath}`;
export const recipeNewView = 'recipe-new';
export const recipeNewValTest = `${recipeNewView}-${validatorPath}`;
export const recipeReadView = 'recipe-read';
export const recipeReadValTest = `${recipeReadView}-${validatorPath}`;
export const recipeEditView = 'recipe-edit';
export const recipeEditValTest = `${recipeEditView}-${validatorPath}`;
export const recipesAll = 'recipes-all';
export const recipesAllValTest = `${recipesAll}-${validatorPath}`;
export const recipeCategories = 'recipes-categories';
export const recipeCategoriesValTest = `${recipeCategories}-${validatorPath}`;

export const userProfileView = 'user-profile';
export const userProfileViewValTest = `${userProfileView}-${validatorPath}`;

export const preLoginViews = 'pre-login';
export const postLoginViews = 'post-login';
export const allViews = 'all';
export const usernameTag = '<username>'
export const recipeIdTag = '<recipe_id>'
/** List of all views */
export const pre_login_views = [
    viewCfg(landingView, false, '/', 'landing view'),
    viewCfg(loginView, false, loginUrl, 'login view'),
    viewCfg(signupView, false, '/accounts/signup/', 'signup view'),
    viewCfg(socialLoginView, false, '/accounts/google/login/', 'social account login view'),
];
export const post_login_views = [
    viewCfg(homeView, true, '/recipes/home/', 'user home'),
    viewCfg(homeValTest, true, `/recipes/${validatorPath}/home/`, 'user home (validater path)'),

    viewCfg(recipeNewView, true, '/recipes/new/', 'create new recipe view'),
    viewCfg(recipeNewValTest, true, `/recipes/${validatorPath}/new/`, 'create new recipe view (validater path)'),
    viewCfg(recipeReadView, true, `/recipes/${recipeIdTag}/`, 'recipe read view'),
    viewCfg(recipeReadValTest, true, `/recipes/${validatorPath}/${recipeIdTag}/`, 'recipe read view (validater path)'),
    viewCfg(recipeEditView, true, `/recipes/${recipeIdTag}/?mode=edit`, 'edit recipe view'),
    viewCfg(recipeEditValTest, true, `/recipes/${validatorPath}/${recipeIdTag}/?mode=edit`, 'edit recipe view (validater path)'),
    viewCfg(recipesAll, true, `/recipes/`, "all recipes view"),
    viewCfg(recipesAllValTest, true, `/recipes/${validatorPath}/`, "all recipes view (validater path)"),
    viewCfg(recipesAll, true, `/recipes/`, "all recipes view"),
    viewCfg(recipesAllValTest, true, `/recipes/${validatorPath}/`, "all recipes view (validater path)"),
    viewCfg(recipeCategories, true, `/recipes/categories/`, "recipes categories view"),
    viewCfg(recipeCategoriesValTest, true, `/recipes/${validatorPath}/categories/`, "recipes categories view (validater path)"),

    viewCfg(userProfileView, true, `/users/${usernameTag}/`, "user's profile view"),
    viewCfg(userProfileViewValTest, true, `/users/${validatorPath}/${usernameTag}/`, "user's profile view (validater path)"),
    viewCfg(logoutView, true, logoutUrl, 'logout view'),
    viewCfg(logoutValTestView, true, `/${validatorPath}/logout/`, 'logout view (validater path)'),
];
export const views = pre_login_views.concat(post_login_views);

export function listViews() {
    const padString = str => `${str}${" ".repeat(35 - str.length)}`;

    console.log(`${padString(allViews)}: all views`)
    console.log(`${padString(preLoginViews)}: all pre-login views`)
    console.log(`${padString(postLoginViews)}: all post-login views`)
    for (const view of views) {
        console.log(`${padString(view.name)}: ${view.desc}`)
    }
    process.exit();
}