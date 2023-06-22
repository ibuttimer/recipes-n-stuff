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
from datetime import datetime

from utils import append_slash, url_path
from .utils import val_test_route_name

APP_NAME = "Recipes 'N' Stuff"
COPYRIGHT_YEAR = 2023
COPYRIGHT = "Ian Buttimer"

# Namespace related
BASE_APP_NAME = "base"
USER_APP_NAME = "user"
PROFILES_APP_NAME = "profiles"
RECIPES_APP_NAME = "recipes"
SUBSCRIPTION_APP_NAME = "subscription"
CHECKOUT_APP_NAME = "checkout"
ORDER_APP_NAME = "order"

# Base routes related
HOME_URL = "/"
HELP_URL = append_slash("help")
ABOUT_URL = append_slash("about")
PRIVACY_URL = append_slash("privacy")
ROBOTS_URL = "robots.txt"
SITEMAP_URL = "sitemap.xml"

HOME_ROUTE_NAME = "home"
HELP_ROUTE_NAME = "help"
ABOUT_ROUTE_NAME = "about"
PRIVACY_ROUTE_NAME = "privacy"
ROBOTS_ROUTE_NAME = "robots.txt"

# Admin routes related
ADMIN_URL = append_slash("admin")

# Accounts routes related
ACCOUNTS_URL = append_slash("accounts")

# mounting allauth on 'accounts' and copying paths from
# allauth/account/urls.py
LOGIN_URL = url_path(ACCOUNTS_URL, "login")
LOGOUT_URL = url_path(ACCOUNTS_URL, "logout")
REGISTER_URL = url_path(ACCOUNTS_URL, "signup")
# excluding mount prefix as used to override allauth
CHANGE_PASSWORD_URL = url_path("password", "change")
MANAGE_EMAIL_URL = url_path(ACCOUNTS_URL, "email")
# copying route names from allauth/account/urls.py
LOGIN_ROUTE_NAME = "account_login"
LOGOUT_ROUTE_NAME = "account_logout"
REGISTER_ROUTE_NAME = "account_signup"
CHANGE_PASSWORD_ROUTE_NAME = "account_change_password"
MANAGE_EMAIL_ROUTE_NAME = "account_email"

# Summernote routes related
SUMMERNOTE_URL = append_slash("summernote")

# User routes related
USERS_URL = append_slash("users")

# Profiles routes related
PROFILES_URL = append_slash("profiles")

# Subscriptions routes related
SUBSCRIPTIONS_URL = append_slash("subscriptions")

# Checkout routes related
CHECKOUT_URL = append_slash("checkout")

# Recipes routes related
RECIPES_URL = append_slash("recipes")

# Orders routes related
ORDERS_URL = append_slash("orders")

# context related
HOME_MENU_CTX = "home_menu"
USER_MENU_CTX = "user_menu"
SIGN_IN_MENU_CTX = "sign_in_menu"
REGISTER_MENU_CTX = "register_menu"
HELP_MENU_CTX = "help_menu"
ABOUT_MENU_CTX = "about_menu"
SUBSCRIPTION_MENU_CTX = "subscription_menu"
MAINTENANCE_MENU_CTX = "maintenance_menu"
RECIPES_MENU_CTX = "recipes_menu"
CATEGORIES_MENU_CTX = "categories_menu"

IS_SUPER_CTX = "is_super"
IS_DEVELOPMENT_CTX = "is_development"
IS_LOW_LEVEL_ADMIN_CTX = "is_low_level_admin"
IS_TEST_CTX = "is_test"
AVATAR_URL_CTX = "avatar_url"
NO_ROBOTS_CTX = "no_robots"

# CSS/HTML validator test related
VAL_TEST_REGISTER_ROUTE_NAME = val_test_route_name(REGISTER_ROUTE_NAME)
VAL_TEST_LOGIN_ROUTE_NAME = val_test_route_name(LOGIN_ROUTE_NAME)
VAL_TEST_LOGOUT_ROUTE_NAME = val_test_route_name(LOGOUT_ROUTE_NAME)

# cloudinary related
AVATAR_FOLDER = "rns_avatars"
IMAGES_FOLDER = "rns_images"

# https://developer.mozilla.org/en-US/docs/Web/Media/Formats/Image_types#common_image_file_types
# Pillow which is used by ImageField in dev mode doesn't support avif or svg
DEV_IMAGE_FILE_TYPES = [
    "image/apng", "image/gif", "image/jpeg", "image/png", "image/webp"
]
IMAGE_FILE_TYPES = DEV_IMAGE_FILE_TYPES.copy()
IMAGE_FILE_TYPES.extend([
    "image/avif", "image/svg+xml"
])

MIN_PASSWORD_LEN = 8

# date the site was last published
LAST_PUBLISH_DATE = datetime(year=2023, month=3, day=9)
