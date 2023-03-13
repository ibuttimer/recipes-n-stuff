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
from typing import Union

from django.db.models import QuerySet

from subscription.constants import THIS_APP
from recipesnstuff.constants import LAST_PUBLISH_DATE
from subscription.constants import (
    SUBSCRIPTIONS_ROUTE_NAME, SUBSCRIPTION_NEW_ROUTE_NAME,
    SUBSCRIPTION_CHOICE_ROUTE_NAME,
)
from utils import (
    reverse_q, namespaced_url, SitemapMixin, SitemapEntry
)


class SubscriptionSitemap(SitemapMixin):
    """
    Sitemap for profiles app
    https://docs.djangoproject.com/en/4.1/ref/contrib/sitemaps/
    """

    def items(self) -> Union[list, str, tuple, QuerySet]:
        """
        Returns a sequence or QuerySet of objects to include in sitemap
        :return:
        """
        return [
            SitemapEntry(location=reverse_q(
                namespaced_url(THIS_APP, SUBSCRIPTIONS_ROUTE_NAME)),
                lastmod=LAST_PUBLISH_DATE, changefreq='yearly', priority=0.6
            ),
            SitemapEntry(location=reverse_q(
                namespaced_url(THIS_APP, SUBSCRIPTION_NEW_ROUTE_NAME)),
                lastmod=LAST_PUBLISH_DATE, changefreq='yearly', priority=0.5
            ),
            SitemapEntry(location=reverse_q(
                namespaced_url(THIS_APP, SUBSCRIPTION_CHOICE_ROUTE_NAME)),
                lastmod=LAST_PUBLISH_DATE, changefreq='daily', priority=0.7
            ),
        ]
