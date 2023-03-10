
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

|     | Browser                                   | OS                          | 
|-----|-------------------------------------------|-----------------------------|
| 1   | Google Chrome, Version 108.0.5359.125     | Windows 11 Pro Version 22H2 |
| 2   | Mozilla Firefox, Version 108.0.1 (64-bit) | Windows 11 Pro Version 22H2 |
| 3   | Opera, Version:94.0.4606.38               | Windows 11 Pro Version 22H2 |

Testing undertaken:

| Feature                                           | Expected                                                                                                                                                                  | Action                                                                                                                                                                                                                                                                             | Related                      | Result                                              | 
|---------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------|-----------------------------------------------------|
| Navbar `Logo`                                     | Clicking opens Landing page                                                                                                                                               | Click `Logo` button                                                                                                                                                                                                                                                                | All pages                    | ![pass](https://badgen.net/badge/checks/Pass/green) |
| Navbar `Help`                                     | Clicking opens Help page                                                                                                                                                  | Click `Help` menu button                                                                                                                                                                                                                                                           | All pages                    | ![pass](https://badgen.net/badge/checks/Pass/green) |
| Registration                                      | Clicking Landing page `Register` and navbar `Register` menu button opens Register page                                                                                    | Click Landing page `Register` and navbar `Register` menu button                                                                                                                                                                                                                    | User registration            | ![pass](https://badgen.net/badge/checks/Pass/green) |
| Registration                                      | User able to manually register after entering all required info                                                                                                           | Enter user info on Registration page                                                                                                                                                                                                                                               | User registration            | ![pass](https://badgen.net/badge/checks/Pass/green) |
| Registration                                      | User able to register using third party account (Google)                                                                                                                  | Click `Sign In` menu button and use `Google` button to register                                                                                                                                                                                                                    | User registration            | ![pass](https://badgen.net/badge/checks/Pass/green) |
| Registration                                      | User able to register using third party account (Twitter)                                                                                                                 | Click Landing page `Sign In` button and use `Twitter` button to register                                                                                                                                                                                                           | User registration            | ![pass](https://badgen.net/badge/checks/Pass/green) |
| User sign in                                      | User able to sign in username and password                                                                                                                                | Click Landing page `Sign In` menu button or navbar `Sign In` menu button and enter credentials                                                                                                                                                                                     | User sign in                 | ![pass](https://badgen.net/badge/checks/Pass/green) |
| User sign out                                     | User able to sign out and cannot access site content (expect `Help`)                                                                                                      | Click navbar `Sign Out` menu button and confirm sign out                                                                                                                                                                                                                           | User sign out                | ![pass](https://badgen.net/badge/checks/Pass/green) |
| User profile                                      | User able to update profile including; bio, avatar and following categories                                                                                               | Click navbar `User -> Profile` menu button and update bio, avatar and following categories                                                                                                                                                                                         | User profile                 | ![pass](https://badgen.net/badge/checks/Pass/green) |


## Responsiveness Testing
Responsiveness testing was done using Google Chrome Developer Tools Device Mode.

Testing undertaken:

| Feature             | Expected                                        | Action      | Related   | Result                                              | 
|---------------------|-------------------------------------------------|-------------|-----------|-----------------------------------------------------|
| Page responsiveness | Page content realigns/resizes when page resized | Resize page | All pages | ![Pass](https://badgen.net/badge/checks/Pass/green) |


## Lighthouse
Lighthouse testing was carried out using a locally installed version of Lighthouse (Version 9.6.6) from an incognito window.

| Page          | Test    | Result                                                                     |                                                                                  |                                                                                      |                                                              | Report                                                                |
|---------------|---------|----------------------------------------------------------------------------|----------------------------------------------------------------------------------|--------------------------------------------------------------------------------------|--------------------------------------------------------------|-----------------------------------------------------------------------|
| Landing       | Mobile  | ![Performance 67](https://img.shields.io/badge/Performance-67-orange)      | ![Accessibility 100](https://img.shields.io/badge/Accessibility-100-brightgreen) | ![Best Practices 100](https://img.shields.io/badge/Best%20Practices-100-brightgreen) | ![SEO 100](https://img.shields.io/badge/SEO-100-brightgreen) | [landing-mobile](doc/test/lighthouse/landing-mobile.html)             |
| Landing       | Desktop | ![Performance 88](https://img.shields.io/badge/Performance-88-orange)      | ![Accessibility 100](https://img.shields.io/badge/Accessibility-100-brightgreen) | ![Best Practices 100](https://img.shields.io/badge/Best%20Practices-100-brightgreen) | ![SEO 100](https://img.shields.io/badge/SEO-100-brightgreen) | [landing-desktop](doc/test/lighthouse/landing-desktop.html)           |
| Sign in       | Mobile  | ![Performance 92](https://img.shields.io/badge/Performance-92-brightgreen) | ![Accessibility 100](https://img.shields.io/badge/Accessibility-100-brightgreen) | ![Best Practices 100](https://img.shields.io/badge/Best%20Practices-100-brightgreen) | ![SEO 100](https://img.shields.io/badge/SEO-100-brightgreen) | [signin-mobile](doc/test/lighthouse/signin-mobile.html)               |
| Sign in       | Desktop | ![Performance 97](https://img.shields.io/badge/Performance-97-brightgreen) | ![Accessibility 100](https://img.shields.io/badge/Accessibility-100-brightgreen) | ![Best Practices 100](https://img.shields.io/badge/Best%20Practices-100-brightgreen) | ![SEO 100](https://img.shields.io/badge/SEO-100-brightgreen) | [signin-desktop](doc/test/lighthouse/signin-desktop.html)             |
| Register      | Mobile  | ![Performance 87](https://img.shields.io/badge/Performance-87-orange)      | ![Accessibility 100](https://img.shields.io/badge/Accessibility-100-brightgreen) | ![Best Practices 100](https://img.shields.io/badge/Best%20Practices-100-brightgreen) | ![SEO 100](https://img.shields.io/badge/SEO-100-brightgreen) | [register-mobile](doc/test/lighthouse/register-mobile.html)           |
| Register      | Desktop | ![Performance 98](https://img.shields.io/badge/Performance-98-brightgreen) | ![Accessibility 100](https://img.shields.io/badge/Accessibility-100-brightgreen) | ![Best Practices 100](https://img.shields.io/badge/Best%20Practices-100-brightgreen) | ![SEO 100](https://img.shields.io/badge/SEO-100-brightgreen) | [register-desktop](doc/test/lighthouse/register-desktop.html)         |
| User profile  | Mobile  | ![Performance 76](https://img.shields.io/badge/Performance-76-orange)      | ![Accessibility 97](https://img.shields.io/badge/Accessibility-97-brightgreen)   | ![Best Practices 100](https://img.shields.io/badge/Best%20Practices-100-brightgreen) | ![SEO 100](https://img.shields.io/badge/SEO-100-brightgreen) | [profile-mobile](doc/test/lighthouse/profile-mobile.html)             |
| User profile  | Desktop | ![Performance 98](https://img.shields.io/badge/Performance-98-brightgreen) | ![Accessibility 98](https://img.shields.io/badge/Accessibility-98-brightgreen)   | ![Best Practices 100](https://img.shields.io/badge/Best%20Practices-100-brightgreen) | ![SEO 100](https://img.shields.io/badge/SEO-100-brightgreen) | [profile-desktop](doc/test/lighthouse/profile-desktop.html)           |
| Logout        | Mobile  | ![Performance 89](https://img.shields.io/badge/Performance-89-orange)      | ![Accessibility 100](https://img.shields.io/badge/Accessibility-100-brightgreen) | ![Best Practices 92](https://img.shields.io/badge/Best%20Practices-92-brightgreen)   | ![SEO 100](https://img.shields.io/badge/SEO-100-brightgreen) | [signout-mobile](doc/test/lighthouse/signout-mobile.html)             |
| Logout        | Desktop | ![Performance 97](https://img.shields.io/badge/Performance-97-brightgreen) | ![Accessibility 100](https://img.shields.io/badge/Accessibility-100-brightgreen) | ![Best Practices 100](https://img.shields.io/badge/Best%20Practices-100-brightgreen) | ![SEO 100](https://img.shields.io/badge/SEO-100-brightgreen) | [signout-desktop](doc/test/lighthouse/signout-desktop.html)           |


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
>
> Consequently, these elements have been excluded (via test-specific urls) from the page content tested to produce the results in the following table.

Where possible content was validated via the URI methods provided by the validators. However this was not possible for pages which required the client to be logged in.
In this case, the content (accessed via special test urls to exclude Bootstrap and Font Awesome css files) was scraped using [scrape.js](data/scrape.js) and saved in the [doc/test/generated](doc/test/generated) folder.
The resultant file was used to validate the content via the file upload methods provided by the validators.

| Page                                 | HTML                                                                                                                                                 | HTML Result                                         | CSS                                                                                                                                                                                                       | Scrape args <sup>**</sup><br>(Excluding host & credentials) | Scraped file                                                                                           | CSS Result                                          |
|--------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------|--------------------------------------------------------------------------------------------------------|-----------------------------------------------------|
| Landing                              | [W3C validator](https://validator.w3.org/nu/?doc=https%3A%2F%2Fsoapbox-opinions.herokuapp.com%2F&showsource=yes&showoutline=yes)                     | ![pass](https://badgen.net/badge/checks/Pass/green) | [(Jigsaw) validator](https://jigsaw.w3.org/css-validator/validator?uri=https%3A%2F%2Fsoapbox-opinions.herokuapp.com%2Fval-test&profile=css3svg&usermedium=all&warning=1&vextwarning=&lang=en)             | n/a                                                         | n/a                                                                                                    | ![pass](https://badgen.net/badge/checks/Pass/green) |
| Sign in                              | [W3C validator](https://validator.w3.org/nu/?showsource=yes&showoutline=yes&doc=https%3A%2F%2Fsoapbox-opinions.herokuapp.com%2Faccounts%2Flogin%2F)  | ![pass](https://badgen.net/badge/checks/Pass/green) | [(Jigsaw) validator](https://jigsaw.w3.org/css-validator/validator?uri=https%3A%2F%2Fsoapbox-opinions.herokuapp.com%2Fval-test%2Flogin%2F&profile=css3svg&usermedium=all&warning=1&vextwarning=&lang=en)  | n/a                                                         | n/a                                                                                                    | ![pass](https://badgen.net/badge/checks/Pass/green) |
| Register                             | [W3C validator](https://validator.w3.org/nu/?showsource=yes&showoutline=yes&doc=https%3A%2F%2Fsoapbox-opinions.herokuapp.com%2Faccounts%2Fsignup%2F) | ![pass](https://badgen.net/badge/checks/Pass/green) | [(Jigsaw) validator](https://jigsaw.w3.org/css-validator/validator?uri=https%3A%2F%2Fsoapbox-opinions.herokuapp.com%2Fval-test%2Fsignup%2F&profile=css3svg&usermedium=all&warning=1&vextwarning=&lang=en) | n/a                                                         | n/a                                                                                                    | ![pass](https://badgen.net/badge/checks/Pass/green) |
| User profile                         | W3C validator <sup>*</sup>                                                                                                                           | ![pass](https://badgen.net/badge/checks/Pass/green) | (Jigsaw) validator <sup>*</sup>                                                                                                                                                                           | -v user-profile-val-test                                    | [user-profile-val-test.html](generated/user-profile-val-test.html)                                     | ![pass](https://badgen.net/badge/checks/Pass/green) |
| Logout                               | W3C validator <sup>*</sup>                                                                                                                           | ![pass](https://badgen.net/badge/checks/Pass/green) | (Jigsaw) validator <sup>*</sup>                                                                                                                                                                           | -v logout-val-test                                          | [logout-val-test.html](generated/logout-val-test.html)                                                 | ![pass](https://badgen.net/badge/checks/Pass/green) |
| Following feed                       | W3C validator <sup>*</sup>                                                                                                                           | ![pass](https://badgen.net/badge/checks/Pass/green) | (Jigsaw) validator <sup>*</sup>                                                                                                                                                                           | -v following-val-test                                       | [following-val-test.html](generated/following-val-test.html)                                           | ![pass](https://badgen.net/badge/checks/Pass/green) |
| Category feed                        | W3C validator <sup>*</sup>                                                                                                                           | ![pass](https://badgen.net/badge/checks/Pass/green) | (Jigsaw) validator <sup>*</sup>                                                                                                                                                                           | -v category-val-test                                        | [category-val-test.html](generated/category-val-test.html)                                             | ![pass](https://badgen.net/badge/checks/Pass/green) |
| Read opinion                         | W3C validator <sup>*</sup>                                                                                                                           | ![pass](https://badgen.net/badge/checks/Pass/green) | (Jigsaw) validator <sup>*</sup>                                                                                                                                                                           | -v opinion-read-val-test --io 40                            | [opinion-read-val-test.html](generated/opinion-read-val-test.html)                                     | ![pass](https://badgen.net/badge/checks/Pass/green) |
| Opinion list                         | W3C validator <sup>*</sup>                                                                                                                           | ![pass](https://badgen.net/badge/checks/Pass/green) | (Jigsaw) validator <sup>*</sup>                                                                                                                                                                           | -v opinions-all-val-test                                    | [opinions-all-val-test.html](generated/opinions-all-val-test.html)                                     | ![pass](https://badgen.net/badge/checks/Pass/green) |
| New opinion                          | W3C validator <sup>*</sup>                                                                                                                           | ![pass](https://badgen.net/badge/checks/Pass/green) | (Jigsaw) validator <sup>*</sup>                                                                                                                                                                           | -v opinion-new-val-test                                     | [opinion-new-val-test.html](generated/opinion-new-val-test.html)                                       | ![pass](https://badgen.net/badge/checks/Pass/green) |
| Edit opinion                         | W3C validator <sup>*</sup>                                                                                                                           | ![pass](https://badgen.net/badge/checks/Pass/green) | (Jigsaw) validator <sup>*</sup>                                                                                                                                                                           | -v opinion-edit-val-test --io 33                            | [opinion-edit-val-test.html](generated/opinion-edit-val-test.html)                                     | ![pass](https://badgen.net/badge/checks/Pass/green) |
| Comment list                         | W3C validator <sup>*</sup>                                                                                                                           | ![pass](https://badgen.net/badge/checks/Pass/green) | (Jigsaw) validator <sup>*</sup>                                                                                                                                                                           | -v comments-all-val-test                                    | [comments-all-val-test.html](generated/comments-all-val-test.html)                                     | ![pass](https://badgen.net/badge/checks/Pass/green) |
| Moderator review pending list        | W3C validator <sup>*</sup>                                                                                                                           | ![pass](https://badgen.net/badge/checks/Pass/green) | (Jigsaw) validator <sup>*</sup>                                                                                                                                                                           | -v mod-opinions-pending-val-test                            | [mod-opinions-pending-val-test.html](generated/mod-opinions-pending-val-test.html)                     | ![pass](https://badgen.net/badge/checks/Pass/green) |
| Moderator review pending pre-assign  | W3C validator <sup>*</sup>                                                                                                                           | ![pass](https://badgen.net/badge/checks/Pass/green) | (Jigsaw) validator <sup>*</sup>                                                                                                                                                                           | -v mod-opinion-review-pre-assign-val-test --po 51           | [mod-opinion-review-pre-assign-val-test.html](generated/mod-opinion-review-pre-assign-val-test.html)   | ![pass](https://badgen.net/badge/checks/Pass/green) |
| Moderator review pending post-assign | W3C validator <sup>*</sup>                                                                                                                           | ![pass](https://badgen.net/badge/checks/Pass/green) | (Jigsaw) validator <sup>*</sup>                                                                                                                                                                           | -v mod-opinion-review-post-assign-val-test --uo 55          | [mod-opinion-review-post-assign-val-test.html](generated/mod-opinion-review-post-assign-val-test.html) | ![pass](https://badgen.net/badge/checks/Pass/green) |

<sup>*</sup> Link not available as not being logged results in redirect to login page

<sup>**</sup> See [Content scraping](#content-scraping)

### Content scraping


## Issues

Issues were logged in [GitHub Issues](https://github.com/ibuttimer/recipes-n-stuff/issues).

#### Bug

[Bug list](https://github.com/ibuttimer/recipes-n-stuff/labels/bug)

The list of open bugs at the end of the project is:

| Title                                                                                                               | Labels  | Description                                                                                      |
|---------------------------------------------------------------------------------------------------------------------|---------|--------------------------------------------------------------------------------------------------|
