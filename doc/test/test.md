
# Testing

## Pre-test setup
### Users

### Database
Populate the database

## Environment
If using a [Virtual Environment](../../README.md#virtual-environment), ensure it is activated. Please see [Activating a virtual environment](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/#activating-a-virtual-environment).

## Tests
Three separate testing frameworks are utilised [pytest](#pytest-unit-testing), [Django Test Tools](#django-test-tools-unit-testing)
and [Jest Unit Testing](#jest-unit-testing).

> **Note:** Tests are _**not**_ interoperable between test frameworks. See [Unit Testing Summary](#unit-testing-summary) for comparison.

### Test Setup
**Note 1:** [Environment](#environment)

**It is necessary to specify a number of environment variables prior to running tests.**
The [.test-env](.test-env) configuration file provides the necessary settings, and may be utilised by setting the `ENV_FILE` environment variable.
```shell
Powershell                     Windows                      Linux
> $env:ENV_FILE='.test-env'    > set ENV_FILE=.test-env    > export ENV_FILE='.test-env'
```
In addition, see [PEP8 Testing](#pep8-testing) for details of how to skip PEP8 testing.

The site was tested using the following methods:

### pytest Unit Testing
Unit testing of scripts was undertaken using [pytest](https://docs.pytest.org/).
The test scripts are located in the [tests](../../tests/) folder, and the naming format is `*_test.py`.

**Note:** [PEP8](https://peps.python.org/pep-0008/) testing is included in the test suite, to disable the PEP8 test see [PEP8 Testing](#pep8-testing)

The tests may be run from the project root folder:
```shell
Run all tests
> pytest

Run an individual test, e.g.
> pytest tests\profiles\dto_test.py
```

### Django Test Tools Unit Testing
Unit testing of views was undertaken using [Django Test Tools](https://docs.djangoproject.com/en/4.1/topics/testing/tools/).
The test scripts are located in the [django_tests](../../django_tests/) folder, and the naming format is `test_*.py`.

The tests may be run from the project root folder:
```shell
Run all tests
> python manage.py test

Run an individual test, e.g.
> python manage.py test django_tests.base.test_landing_view
```

## Jest Unit Testing
Javascript unit testing was undertaken using [Jest](https://jestjs.io/), combined with [Puppeteer](https://pptr.dev/) to
provide the browser automation to retrieve the page content.

The test scripts are located in the [jest_tests](../../jest_tests/) folder, and the naming format is `*.spec.js`.

### Jest Unit Testing Setup
**Note 1:** [Environment](#environment)

**Note 2:** The test server need to be running prior to executing tests.

Create a configuration file called `test_config.json` in the [jest_tests](../../jest_tests/) folder, based on [sample_test_config.json](../../jest_tests/sample_test_config.json)

The tests may be run from the project root folder:
```shell
Run all tests
> npm test
```

## Test Coverage
Test coverage reports are generated using the [coverage](https://pypi.org/project/coverage/) utility, ands its configuration is specified in [.coveragerc](../../.coveragerc).
See [pytest](#pytest-unit-testing) for usage.

### Test Coverage Reports

| Framework                                            | Report                                                           |
|------------------------------------------------------|------------------------------------------------------------------|
| [pytest](#pytest-unit-testing)                       | [pytest test coverage report](doc/test/pytest_report/index.html) |
| [Django Test Tools](#django-test-tools-unit-testing) | [Django test coverage report](doc/test/django_report/index.html) |
| [Jest Unit Testing](#jest-unit-testing)              | n/a as testing was performed using automated browser interaction |

## Unit Testing Summary

| Environment                 | [pytest](#pytest-unit-testing)                                                  | [Django Test Tools](#django-test-tools-unit-testing)                            | [Jest Unit Testing](#jest-unit-testing)             |
|-----------------------------|---------------------------------------------------------------------------------|---------------------------------------------------------------------------------|-----------------------------------------------------|
| **Location**                | [tests](../../tests/)                                                           | [django_tests](../../django_tests/)                                             | [jest_tests](../../jest_tests/)                     |
| **Naming style**            | `*_test.py`                                                                     | `test_*.py`                                                                     | `*.spec.js`                                         |
| **Setup**                   | [Test Setup](#test-setup)                                                       | [Test Setup](#test-setup)                                                       | [Jest Unit Testing Setup](#jest-unit-testing-setup) |
| **Command**                 | `pytest`                                                                        | `python manage.py test`                                                         | `npm test`                                          |
| **Coverage command**        | `coverage run -m pytest`                                                        | `coverage run manage.py test`                                                   | n/a                                                 |
| **Coverage report command** | `coverage html -d doc/test/pytest_report --title="pytest test coverage report"` | `coverage html -d doc/test/django_report --title="Django test coverage report"` | n/a                                                 |
| **Reported coverage**       | Unittest test coverage report: tbc%                                             | Django test coverage report: tbc%                                               | ![pass](https://badgen.net/badge/checks/Pass/green) |



## PEP8 Testing
[PEP8](https://peps.python.org/pep-0008/) compliance testing was performed using [pycodestyle](https://pypi.org/project/pycodestyle/)

**Note:** [Environment](#environment)

The tests may be run from the project root folder:
```shell
Run all tests
> pycodestyle .

Run an individual test, e.g.
> pycodestyle user/forms.py 
```

The basic pycodestyle configuration is contained in [setup.cfg](../../setup.cfg). See [Configuration](https://pycodestyle.pycqa.org/en/latest/intro.html#configuration) for additional configuration options.

> **Note:** PEP8 testing is also performed as part of the unit test suite, see [test_style.py](../../tests/style_test.py).
> When running unit tests from the terminal, it may be disabled by setting the `SKIP_PEP8` environment variable to `y` or `n`.

```shell
Powershell                     Windows                      Linux and Mac
> $env:SKIP_PEP8='y'           > set SKIP_PEP8=y            > export SKIP_PEP8='y'
```

## Manual
The site was manually tested in the following browsers:

|     | Browser                                  | OS                          | 
|-----|------------------------------------------|-----------------------------|
| 1   | Google Chrome, Version 111.0.5563.65     | Windows 11 Pro Version 22H2 |
| 2   | Mozilla Firefox, Version 111.0 (64-bit)  | Windows 11 Pro Version 22H2 |
| 3   | Opera, Version:96.0.4693.80              | Windows 11 Pro Version 22H2 |

Testing undertaken:

| Feature                | Expected                                                                                                             | Action                                                                                                                      | Related           | Result                                              | 
|------------------------|----------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------|-------------------|-----------------------------------------------------|
| Navbar `Logo`          | Clicking opens Landing page                                                                                          | Click `Logo` button                                                                                                         | All pages         | ![pass](https://badgen.net/badge/checks/Pass/green) |
| Navbar `Help`          | Clicking opens Help page                                                                                             | Click `Help` menu button                                                                                                    | All pages         | ![pass](https://badgen.net/badge/checks/Pass/green) |
| Navbar `About`         | Clicking opens About page                                                                                            | Click `About` menu button                                                                                                   | All pages         | ![pass](https://badgen.net/badge/checks/Pass/green) |
| Registration           | Clicking Landing page `Register` and navbar `Register` menu button opens Register page                               | Click Landing page `Register` and navbar `Register` menu button                                                             | User registration | ![pass](https://badgen.net/badge/checks/Pass/green) |
| Registration           | User able to manually register after entering all required info                                                      | Enter user info on Registration page                                                                                        | User registration | ![pass](https://badgen.net/badge/checks/Pass/green) |
| Registration           | User able to register using third party account (Google)                                                             | Click `Sign In` menu button and use `Google` button to register                                                             | User registration | ![pass](https://badgen.net/badge/checks/Pass/green) |
| Registration           | User able to register using third party account (Twitter)                                                            | Click Landing page `Sign In` button and use `Twitter` button to register                                                    | User registration | ![pass](https://badgen.net/badge/checks/Pass/green) |
| User sign in           | User able to sign in username and password                                                                           | Click Landing page `Sign In` menu button or navbar `Sign In` menu button and enter credentials                              | User sign in      | ![pass](https://badgen.net/badge/checks/Pass/green) |
| Subscription selection | User able to select and pay for a subscription                                                                       | Sign in, select subscription, billing address and pay                                                                       | User sign in      | ![pass](https://badgen.net/badge/checks/Pass/green) |
| Address creation       | User able to create a new address and mark it as default                                                             | Click `Addresses` in user menu, click `Add address`, enter details and check `Default`                                      | User profile      | ![pass](https://badgen.net/badge/checks/Pass/green) |
| User profile           | User able to update profile including; bio and avatar                                                                | Click navbar `User -> Profile` menu button and update bio and avatar                                                        | User profile      | ![pass](https://badgen.net/badge/checks/Pass/green) |
| View recipes           | User able to view recipes list and individual recipes                                                                | Click navbar `Recipes -> All` menu button and click on a recipe to view                                                     | Content           | ![pass](https://badgen.net/badge/checks/Pass/green) |
| Purchase ingredients   | User able to purchase recipe ingredients and receives confirmation email                                             | Click navbar `Recipes -> All` menu button and click on a recipe to view. Add recipe ingredients to basket and checkout      | E-commerce        | ![pass](https://badgen.net/badge/checks/Pass/green) |
| Review past orders     | User able to view past order and reorder                                                                             | Click navbar `User -> Orders` menu button and click on a non-subscription order to view. Reorder ingredients and checkout   | E-commerce        | ![pass](https://badgen.net/badge/checks/Pass/green) |
| Modify basket          | User able to modify basket item count, delivery option, currency, clear basket and select different delivery address | Add items to basket and modify basket item count, delivery option, clear basket and select different delivery address       | E-commerce        | ![pass](https://badgen.net/badge/checks/Pass/green) |
| Create recipe          | User able to create a recipe                                                                                         | Click navbar `Recipes -> New` menu button and enter recipe details                                                          | Content           | ![pass](https://badgen.net/badge/checks/Pass/green) |
| Edit recipe            | User able to edit their own recipe                                                                                   | Click navbar `Recipes -> Mine` menu button, select a recipe from the list and edit recipe details                           | Content           | ![pass](https://badgen.net/badge/checks/Pass/green) |
| Delete recipe          | User able to delete their own recipe                                                                                 | Click navbar `Recipes -> Mine` menu button, select a recipe from the list and delete the recipe                             | Content           | ![pass](https://badgen.net/badge/checks/Pass/green) |
| Recipe category search | User able to search for recipes by category                                                                          | Click navbar `Recipes -> Categories` menu button, select a category from the list and view a recipe from the resultant list | Content           | ![pass](https://badgen.net/badge/checks/Pass/green) |
| Recipe keyword search  | User able to search for recipes by keyword                                                                           | Enter a keyword in the navbar search form and view a recipe from the resultant list                                         | Content           | ![pass](https://badgen.net/badge/checks/Pass/green) |
| Newsletter signup      | User able to signup for newsletter                                                                                   | Click the subscribe button, enter email address, select email checkbox and click Subscribe                                  | Content           | ![pass](https://badgen.net/badge/checks/Pass/green) |
| User sign out          | User able to sign out and cannot access site content (expect `Help` and `About`)                                     | Click navbar `Sign Out` menu button and confirm sign out                                                                    | User sign out     | ![pass](https://badgen.net/badge/checks/Pass/green) |

## Responsiveness Testing
Responsiveness testing was done using Google Chrome Developer Tools Device Mode.

Testing undertaken:

| Feature             | Expected                                        | Action      | Related   | Result                                              | 
|---------------------|-------------------------------------------------|-------------|-----------|-----------------------------------------------------|
| Page responsiveness | Page content realigns/resizes when page resized | Resize page | All pages | ![Pass](https://badgen.net/badge/checks/Pass/green) |


## Lighthouse
Lighthouse testing was carried out using a locally installed version of Lighthouse (Version 9.6.8) from an incognito window.

| Page         | Test    | Result                                                                     |                                                                                  |                                                                                      |                                                              | Report                                                                   |
|--------------|---------|----------------------------------------------------------------------------|----------------------------------------------------------------------------------|--------------------------------------------------------------------------------------|--------------------------------------------------------------|--------------------------------------------------------------------------|
| Landing      | Mobile  | ![Performance 63](https://img.shields.io/badge/Performance-63-orange)      | ![Accessibility 100](https://img.shields.io/badge/Accessibility-91-brightgreen)  | ![Best Practices 100](https://img.shields.io/badge/Best%20Practices-100-brightgreen) | ![SEO 99](https://img.shields.io/badge/SEO-99-brightgreen)   | [landing-mobile](doc/test/lighthouse/landing-mobile.html)                |
| Landing      | Desktop | ![Performance 80](https://img.shields.io/badge/Performance-80-orange)      | ![Accessibility 100](https://img.shields.io/badge/Accessibility-100-brightgreen) | ![Best Practices 100](https://img.shields.io/badge/Best%20Practices-100-brightgreen) | ![SEO 100](https://img.shields.io/badge/SEO-100-brightgreen) | [landing-desktop](doc/test/lighthouse/landing-desktop.html)              |
| Sign in      | Mobile  | ![Performance 66](https://img.shields.io/badge/Performance-66-orange)      | ![Accessibility 93](https://img.shields.io/badge/Accessibility-93-brightgreen)   | ![Best Practices 100](https://img.shields.io/badge/Best%20Practices-100-brightgreen) | ![SEO 92](https://img.shields.io/badge/SEO-92-brightgreen)   | [signin-mobile](doc/test/lighthouse/signin-mobile.html)                  |
| Sign in      | Desktop | ![Performance 95](https://img.shields.io/badge/Performance-95-brightgreen) | ![Accessibility 100](https://img.shields.io/badge/Accessibility-100-brightgreen) | ![Best Practices 100](https://img.shields.io/badge/Best%20Practices-100-brightgreen) | ![SEO 91](https://img.shields.io/badge/SEO-91-brightgreen)   | [signin-desktop](doc/test/lighthouse/signin-desktop.html)                |
| Register     | Mobile  | ![Performance 87](https://img.shields.io/badge/Performance-69-orange)      | ![Accessibility 92](https://img.shields.io/badge/Accessibility-92-brightgreen)   | ![Best Practices 100](https://img.shields.io/badge/Best%20Practices-100-brightgreen) | ![SEO 92](https://img.shields.io/badge/SEO-92-brightgreen)   | [register-mobile](doc/test/lighthouse/register-mobile.html)              |
| Register     | Desktop | ![Performance 96](https://img.shields.io/badge/Performance-96-brightgreen) | ![Accessibility 100](https://img.shields.io/badge/Accessibility-100-brightgreen) | ![Best Practices 100](https://img.shields.io/badge/Best%20Practices-100-brightgreen) | ![SEO 91](https://img.shields.io/badge/SEO-91-brightgreen)   | [register-desktop](doc/test/lighthouse/register-desktop.html)            |
| User profile | Mobile  | ![Performance 64](https://img.shields.io/badge/Performance-64-orange)      | ![Accessibility 89](https://img.shields.io/badge/Accessibility-89-orange)        | ![Best Practices 100](https://img.shields.io/badge/Best%20Practices-100-brightgreen) | ![SEO 92](https://img.shields.io/badge/SEO-92-brightgreen)   | [profile-mobile](doc/test/lighthouse/profile-mobile.html)                |
| User profile | Desktop | ![Performance 94](https://img.shields.io/badge/Performance-94-brightgreen) | ![Accessibility 91](https://img.shields.io/badge/Accessibility-91-brightgreen)   | ![Best Practices 100](https://img.shields.io/badge/Best%20Practices-100-brightgreen) | ![SEO 91](https://img.shields.io/badge/SEO-91-brightgreen)   | [profile-desktop](doc/test/lighthouse/profile-desktop.html)              |
| Logout       | Mobile  | ![Performance 66](https://img.shields.io/badge/Performance-66-orange)      | ![Accessibility 91](https://img.shields.io/badge/Accessibility-91-brightgreen)   | ![Best Practices 100](https://img.shields.io/badge/Best%20Practices-100-brightgreen) | ![SEO 91](https://img.shields.io/badge/SEO-91-brightgreen)   | [signout-mobile](doc/test/lighthouse/signout-mobile.html)                |
| Logout       | Desktop | ![Performance 95](https://img.shields.io/badge/Performance-95-brightgreen) | ![Accessibility 93](https://img.shields.io/badge/Accessibility-93-brightgreen)   | ![Best Practices 100](https://img.shields.io/badge/Best%20Practices-100-brightgreen) | ![SEO 91](https://img.shields.io/badge/SEO-91-brightgreen)   | [signout-desktop](doc/test/lighthouse/signout-desktop.html)              |
| Recipe home  | Mobile  | ![Performance 61](https://img.shields.io/badge/Performance-61-orange)      | ![Accessibility 91](https://img.shields.io/badge/Accessibility-91-brightgreen)   | ![Best Practices 100](https://img.shields.io/badge/Best%20Practices-100-brightgreen) | ![SEO 100](https://img.shields.io/badge/SEO-100-brightgreen) | [recipe-home-mobile](doc/test/lighthouse/recipe-home-mobile.html)        |
| Recipe home  | Desktop | ![Performance 81](https://img.shields.io/badge/Performance-81-orange)      | ![Accessibility 93](https://img.shields.io/badge/Accessibility-93-brightgreen)   | ![Best Practices 100](https://img.shields.io/badge/Best%20Practices-100-brightgreen) | ![SEO 100](https://img.shields.io/badge/SEO-100-brightgreen) | [recipe-home-desktop](doc/test/lighthouse/recipe-home-desktop.html)      |
| Recipe view  | Mobile  | ![Performance 63](https://img.shields.io/badge/Performance-63-orange)      | ![Accessibility 89](https://img.shields.io/badge/Accessibility-89-orange)        | ![Best Practices 100](https://img.shields.io/badge/Best%20Practices-100-brightgreen) | ![SEO 100](https://img.shields.io/badge/SEO-100-brightgreen) | [recipe-view-mobile](doc/test/lighthouse/recipe-view-mobile.html)        |
| Recipe view  | Desktop | ![Performance 92](https://img.shields.io/badge/Performance-92-brightgreen) | ![Accessibility 90](https://img.shields.io/badge/Accessibility-90-brightgreen)   | ![Best Practices 100](https://img.shields.io/badge/Best%20Practices-100-brightgreen) | ![SEO 100](https://img.shields.io/badge/SEO-100-brightgreen) | [recipe-view-desktop.html](doc/test/lighthouse/recipe-view-desktop.html) |
| Checkout     | Mobile  | ![Performance 61](https://img.shields.io/badge/Performance-61-orange)      | ![Accessibility 86](https://img.shields.io/badge/Accessibility-86-orange)        | ![Best Practices 100](https://img.shields.io/badge/Best%20Practices-100-brightgreen) | ![SEO 91](https://img.shields.io/badge/SEO-91-brightgreen)   | [checkout-mobile](doc/test/lighthouse/checkout-mobile.html)              |
| Checkout     | Desktop | ![Performance 93](https://img.shields.io/badge/Performance-93-brightgreen) | ![Accessibility 87](https://img.shields.io/badge/Accessibility-87-orange)        | ![Best Practices 100](https://img.shields.io/badge/Best%20Practices-100-brightgreen) | ![SEO 91](https://img.shields.io/badge/SEO-91-brightgreen)   | [checkout-desktop.html](doc/test/lighthouse/checkout-desktop.html)       |


## Accessibility
Accessibility testing was carried out using the [NVDA](https://www.nvaccess.org/) and [ChromeVox](https://chrome.google.com/webstore/detail/screen-reader/kgejglhpjiefppelpmljglcjbhoiplfn?hl=en) screen readers.

Testing undertaken:

| Feature           | Expected                                              | Action                           | Related   | Result                                              | 
|-------------------|-------------------------------------------------------|----------------------------------|-----------|-----------------------------------------------------|
| Audio commentary  | Audio commentary provided for important page elements | Process page using screen reader | All pages | ![Pass](https://badgen.net/badge/checks/Pass/green) |

## User
User testing issues were logged in [GitHub Issues](https://github.com/ibuttimer/recipes-n-stuff/issues?q=is%3Aissue+label%3A%22user+test%22) and identified the following issues/enhancements:

| Issue                                                                                                      | Label                                | Description                                                                                                                                        |
|------------------------------------------------------------------------------------------------------------|--------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------|



## Validator Testing

The [W3C Nu Html Checker](https://validator.w3.org/nu/) was utilised to check the HTML validity, while the [W3C CSS Validation Service](https://jigsaw.w3.org/css-validator/) was utilised to check the CSS validity with respect to [CSS level 3 + SVG](https://www.w3.org/Style/CSS/current-work.html.)

> **Note:** The following third party artifacts fail the W3C Validator tests:
> - [W3C CSS Validation Service](https://jigsaw.w3.org/css-validator/) checks
>   - [Bootstrap v5.2.3](https://www.jsdelivr.com/package/npm/bootstrap) minified css files
>   - [Font Awesome](https://github.com/FortAwesome/Font-Awesome) minified css files
> - [W3C Nu Html Checker](https://validator.w3.org/nu/)
>   - [django-summernote](https://pypi.org/project/django-summernote/) HTML
>   - [Stripe](https://pypi.org/project/stripe/) HTML
>   - [Mailchimp](https://mailchimp.com/) HTML
>
> Consequently, these elements have been excluded (via test-specific urls) from the page content tested to produce the results in the following table.

Where possible content was validated via the URI methods provided by the validators. However, this was not possible for pages which required the client to be logged in.
In this case, the content (accessed via special test urls to exclude Bootstrap and Font Awesome css files) was scraped using [scrape.js](data/scrape.js) and saved in the [doc/test/generated](doc/test/generated) folder.
The resultant file was used to validate the content via the file upload methods provided by the validators.

| Page              | HTML                                                                                                                                                             | HTML Result                                         | CSS                                                                                                                                                                                                     | Scrape args <sup>**</sup><br>(Excluding host & credentials) | Scraped file                                                                   | Test url                                                            | CSS Result                                          |
|-------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------|--------------------------------------------------------------------------------|---------------------------------------------------------------------|-----------------------------------------------------|
| Landing           | [W3C validator](https://validator.w3.org/nu/?showsource=yes&showoutline=yes&doc=https%3A%2F%2Frecipesnstuff.herokuapp.com%2Fval-test%2F)                         | ![pass](https://badgen.net/badge/checks/Pass/green) | [(Jigsaw) validator](https://jigsaw.w3.org/css-validator/validator?uri=https%3A%2F%2Frecipesnstuff.herokuapp.com%2Fval-test%2F&profile=css3svg&usermedium=all&warning=1&vextwarning=&lang=en)           | n/a                                                         | n/a                                                                            | https://recipesnstuff.herokuapp.com/val-test/                       | ![pass](https://badgen.net/badge/checks/Pass/green) |
| Sign in           | [W3C validator](https://validator.w3.org/nu/?showsource=yes&showoutline=yes&doc=https%3A%2F%2Frecipesnstuff.herokuapp.com%2Faccounts%2Flogin%2F)<sup>***</sup>   | ![pass](https://badgen.net/badge/checks/Pass/green) | [(Jigsaw) validator](https://jigsaw.w3.org/css-validator/validator?uri=https%3A%2F%2Frecipesnstuff.herokuapp.com%2Fval-test%2Flogin%2F&profile=css3svg&usermedium=all&warning=1&vextwarning=&lang=en)   | n/a                                                         | n/a                                                                            | https://recipesnstuff.herokuapp.com/accounts/login/                 | ![pass](https://badgen.net/badge/checks/Pass/green) |
| Register          | [W3C validator](https://validator.w3.org/nu/?showsource=yes&showoutline=yes&doc=https%3A%2F%2Frecipesnstuff.herokuapp.com%2Faccounts%2Fsignup%2F)<sup>***</sup>  | ![pass](https://badgen.net/badge/checks/Pass/green) | [(Jigsaw) validator](https://jigsaw.w3.org/css-validator/validator?uri=https%3A%2F%2Frecipesnstuff.herokuapp.com%2Fval-test%2Fsignup%2F&profile=css3svg&usermedium=all&warning=1&vextwarning=&lang=en)  | n/a                                                         | n/a                                                                            | https://recipesnstuff.herokuapp.com/accounts/signup/                | ![pass](https://badgen.net/badge/checks/Pass/green) |
| User profile      | W3C validator <sup>*</sup>                                                                                                                                       | ![pass](https://badgen.net/badge/checks/Pass/green) | (Jigsaw) validator <sup>*</sup>                                                                                                                                                                         | -v user-profile-val-test                                    | [user-profile-val-test.html](generated/user-profile-val-test.html)             | https://recipesnstuff.herokuapp.com/users/val-test/user1/           | ![pass](https://badgen.net/badge/checks/Pass/green) |
| Logout            | W3C validator <sup>*</sup>                                                                                                                                       | ![pass](https://badgen.net/badge/checks/Pass/green) | (Jigsaw) validator <sup>*</sup>                                                                                                                                                                         | -v logout-val-test                                          | [logout-val-test.html](generated/logout-val-test.html)                         | https://recipesnstuff.herokuapp.com/val-test/logout/                | ![pass](https://badgen.net/badge/checks/Pass/green) |
| Create recipe     | W3C validator <sup>*</sup>                                                                                                                                       | ![pass](https://badgen.net/badge/checks/Pass/green) | (Jigsaw) validator <sup>*</sup>                                                                                                                                                                         | -v recipe-new-val-test                                      | [recipe-new-val-test.html](generated/recipe-new-val-test.html)                 | https://recipesnstuff.herokuapp.com/recipes/val-test/new/           | ![pass](https://badgen.net/badge/checks/Pass/green) |
| Recipe read       | W3C validator <sup>*</sup>                                                                                                                                       | ![pass](https://badgen.net/badge/checks/Pass/green) | (Jigsaw) validator <sup>*</sup>                                                                                                                                                                         | -v recipe-read-val-test --ir 301                            | [recipe-read-val-test.html](generated/recipe-read-val-test.html)               | https://recipesnstuff.herokuapp.com/recipes/val-test/301/           | ![pass](https://badgen.net/badge/checks/Pass/green) |
| Recipe edit       | W3C validator <sup>*</sup>                                                                                                                                       | ![pass](https://badgen.net/badge/checks/Pass/green) | (Jigsaw) validator <sup>*</sup>                                                                                                                                                                         | -v recipe-edit-val-test --ir 301                            | [recipe-edit-val-test.html](generated/recipe-edit-val-test.html)               | https://recipesnstuff.herokuapp.com/recipes/val-test/301/?mode=edit | ![pass](https://badgen.net/badge/checks/Pass/green) |
| Recipe list       | W3C validator <sup>*</sup>                                                                                                                                       | ![pass](https://badgen.net/badge/checks/Pass/green) | (Jigsaw) validator <sup>*</sup>                                                                                                                                                                         | -v recipes-all-val-test                                     | [recipes-all-val-test.html](generated/recipes-all-val-test.html)               | https://recipesnstuff.herokuapp.com/recipes/val-test/               | ![pass](https://badgen.net/badge/checks/Pass/green) |
| Recipe categories | W3C validator <sup>*</sup>                                                                                                                                       | ![pass](https://badgen.net/badge/checks/Pass/green) | (Jigsaw) validator <sup>*</sup>                                                                                                                                                                         | -v recipes-categories-val-test                              | [recipes-categories-val-test.html](generated/recipes-categories-val-test.html) | https://recipesnstuff.herokuapp.com/recipes/val-test/categories/    | ![pass](https://badgen.net/badge/checks/Pass/green) |

<sup>*</sup> Link not available as not being logged results in redirect to login page

<sup>**</sup> See [Content scraping](#content-scraping)

<sup>***</sup> Unnecessary type attribute warning generated for Mailchimp embedded javascript


### Content scraping
The [scrape.js](data/scrape.js) script may be used to scrape page content.
It is provided so that content requiring the client to be logged in may be retrieved quickly with minimal manual user input.

From the [data](data) folder run the following
```bash
# Help listing
node .\scrape.js --help
 
# List if views which may be scraped 
node .\scrape.js -l

# E.g. scrape logout page (replace 'user' and 'password' as appropriate 
node .\scrape.js -b https://recipesnstuff.herokuapp.com/ -u user -p password -v logout-val-test
```


## Issues

Issues were logged in [GitHub Issues](https://github.com/ibuttimer/recipes-n-stuff/issues).

#### Bug

[Bug list](https://github.com/ibuttimer/recipes-n-stuff/labels/bug)

The list of open bugs at the end of the project is:

| Title                                                                                                               | Labels  | Description                                                                                      |
|---------------------------------------------------------------------------------------------------------------------|---------|--------------------------------------------------------------------------------------------------|
