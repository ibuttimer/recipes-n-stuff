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

from .constants import (
    BASE_APP_NAME, USER_APP_NAME, PROFILES_APP_NAME, RECIPES_APP_NAME,
    SUBSCRIPTION_APP_NAME, CHECKOUT_APP_NAME,
    ADMIN_URL, ACCOUNTS_URL, SUMMERNOTE_URL, USERS_URL,
    IMAGE_FILE_TYPES, DEV_IMAGE_FILE_TYPES, MIN_PASSWORD_LEN,
    AVATAR_FOLDER, IMAGES_FOLDER, HOME_ROUTE_NAME
)
from .settings import DEVELOPMENT, TEST, LOW_LEVEL_ADMIN
from .utils import val_test_route_name, val_test_url, VAL_TEST_PATH_PREFIX

__all__ = [
    'BASE_APP_NAME',
    'USER_APP_NAME',
    'PROFILES_APP_NAME',
    'RECIPES_APP_NAME',
    'SUBSCRIPTION_APP_NAME',
    'CHECKOUT_APP_NAME',
    'ADMIN_URL',
    'ACCOUNTS_URL',
    'SUMMERNOTE_URL',
    'USERS_URL',
    'IMAGE_FILE_TYPES',
    'DEV_IMAGE_FILE_TYPES',
    'MIN_PASSWORD_LEN',
    'AVATAR_FOLDER',
    'IMAGES_FOLDER',
    'HOME_ROUTE_NAME',
    'DEVELOPMENT',
    'TEST',
    'LOW_LEVEL_ADMIN',

    'val_test_route_name',
    'val_test_url',
    'VAL_TEST_PATH_PREFIX',
]
