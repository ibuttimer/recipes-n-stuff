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
from collections import namedtuple
from datetime import datetime

from django.contrib.sitemaps import Sitemap


SitemapEntry = namedtuple(
    'SitemapEntry', ['location', 'lastmod', 'changefreq', 'priority'],
    defaults=[None, None, None, None])


class SitemapMixin(Sitemap):
    """
    Sitemap Mixin
    https://docs.djangoproject.com/en/4.1/ref/contrib/sitemaps/
    """

    def lastmod(self, obj) -> datetime:
        """
        Return last-modified date/time for every object returned by items()
        :param obj:
        :return:
        """
        return obj.lastmod

    def location(self, obj):
        """
        Return the absolute path for a given object
        :param obj:
        :return:
        """
        return obj.location

    def changefreq(self, obj):
        """
        Return the change frequency for a given object
        :param obj:
        :return:
        """
        return obj.changefreq

    def priority(self, obj):
        """
        Return the priority for a given object
        :param obj:
        :return:
        """
        return obj.priority
