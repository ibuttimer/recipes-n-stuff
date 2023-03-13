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
from typing import Union

from django.contrib.sitemaps import Sitemap
from django.db.models import QuerySet

from recipes.constants import (
    THIS_APP, RECIPE_ID_ROUTE_NAME, RECIPES_ROUTE_NAME
)
from recipes.models import Recipe
from recipesnstuff.constants import LAST_PUBLISH_DATE
from utils import (
    reverse_q, namespaced_url, DATE_NEWEST_LOOKUP, SitemapMixin, SitemapEntry
)


class RecipeSitemap(SitemapMixin):
    """
    Sitemap for recipe app
    https://docs.djangoproject.com/en/4.1/ref/contrib/sitemaps/
    """

    def items(self) -> Union[list, str, tuple, QuerySet]:
        """
        Returns a sequence or QuerySet of objects to include in sitemap
        :return:
        """
        return [
            SitemapEntry(location=reverse_q(
                namespaced_url(THIS_APP, RECIPES_ROUTE_NAME)),
                lastmod=Recipe.objects.order_by(
                    f'{DATE_NEWEST_LOOKUP}{Recipe.DATE_PUBLISHED_FIELD}'
                ).first().date_published
                if Recipe.objects.exists() else LAST_PUBLISH_DATE,
                changefreq='daily', priority=0.8
            ),
        ]


class IndividualRecipeSitemap(Sitemap):
    """
    Sitemap for recipe app
    https://docs.djangoproject.com/en/4.1/ref/contrib/sitemaps/
    """
    changefreq = "never"
    priority = 0.8

    def items(self) -> Union[list, str, tuple, QuerySet]:
        """
        Returns a sequence or QuerySet of objects to include in sitemap
        :return:
        """
        return Recipe.objects.all()

    def lastmod(self, obj) -> datetime:
        """
        Return last-modified date/time for every object returned by items()
        :param obj:
        :return:
        """
        return obj.date_published

    def location(self, obj):
        """
        Return the absolute path for a given object
        :param obj:
        :return:
        """
        return reverse_q(
            namespaced_url(THIS_APP, RECIPE_ID_ROUTE_NAME),
            args=[obj.id]
        )
