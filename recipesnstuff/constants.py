#  MIT License
#
#  Copyright (c) 2023 Ian Buttimer
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to
#  deal in the Software without restriction, including without limitation the
#  rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
#  sell copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#  FROM,OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#  DEALINGS IN THE SOFTWARE.

APP_NAME = "Recipes 'N' Stuff"
COPYRIGHT_YEAR = 2023
COPYRIGHT = "Ian Buttimer"

# Namespace related
BASE_APP_NAME = "base"

# Request methods
GET = 'GET'
PATCH = 'PATCH'
POST = 'POST'
DELETE = 'DELETE'

# Base routes related
HOME_URL = "/"

HOME_ROUTE_NAME = "home"
HELP_ROUTE_NAME = "help"
LANDING_ROUTE_NAME = "landing"

# context related
HOME_MENU_CTX = "home_menu"
USER_MENU_CTX = "user_menu"
SIGN_IN_MENU_CTX = "sign_in_menu"
REGISTER_MENU_CTX = "register_menu"
HELP_MENU_CTX = "help_menu"

IS_SUPER_CTX = "is_super"
IS_MODERATOR_CTX = "is_moderator"
IS_DEVELOPMENT_CTX = "is_development"
IS_TEST_CTX = "is_test"

MIN_PASSWORD_LEN = 8
