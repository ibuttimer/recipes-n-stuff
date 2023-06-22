#  MIT License
#
#  Copyright (c) 2022 Ian Buttimer
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
#

from collections import namedtuple

from django.http import HttpRequest

from .constants import (
    COPYRIGHT_YEAR, COPYRIGHT, IS_DEVELOPMENT_CTX, IS_LOW_LEVEL_ADMIN_CTX,
    IS_TEST_CTX
)
from .settings import (
    DEVELOPMENT, LOW_LEVEL_ADMIN, TEST, GOOGLE_SITE_VERIFICATION,
    FOOD_DOT_COM, FACEBOOK_PAGE
)

Social = namedtuple("Social", ["name", "icon", "url"])


def footer_context(request: HttpRequest) -> dict:
    """
    Context processor providing basic footer info
    :param request: http request
    :return: dictionary to add to template context
    """
    context = {
        "copyright_year": COPYRIGHT_YEAR,
        "copyright": COPYRIGHT,
        "socials": [
            Social("Facebook", "fa-brands fa-square-facebook",
                   FACEBOOK_PAGE),
            Social("Twitter", "fa-brands fa-square-twitter",
                   "https://twitter.com"),
            Social("Instagram", "fa-brands fa-square-instagram",
                   "https://instagram.com"),
        ],
        IS_DEVELOPMENT_CTX: DEVELOPMENT,
        IS_LOW_LEVEL_ADMIN_CTX: LOW_LEVEL_ADMIN,
        IS_TEST_CTX: TEST,
        "google_site_verification": GOOGLE_SITE_VERIFICATION,
        "food_dot_com": FOOD_DOT_COM
    }
    return context
