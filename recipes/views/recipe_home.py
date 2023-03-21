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
from random import choice, randint
from string import capwords

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.templatetags.static import static
from django.views.decorators.http import require_http_methods

from base.views import CarouselItem, CAROUSEL_LIST_CTX
from .dto import RecipeDto
from .recipe_queries import (
    get_recipe_by_category_keyword
)
from ..constants import (
    THIS_APP, TAGLINE_CTX, RECIPE_LIST_CTX
)
from utils import (
    Crud, app_template_path, TITLE_CTX, GET
)
from .utils import recipe_permission_check

TITLE = 'Home'

TAGLINES = [
    "{} tonight?", "Craving {}?", "How about {}?",
]
SEARCH_TERMS = [
    'chicken', 'beef', 'tuna', 'vegan'
]
RECIPES_PER_PAGE = 2


@login_required
@require_http_methods([GET])
def recipe_home(request: HttpRequest) -> HttpResponse:
    """
    View function to display recipe home page
    :param request: http request
    :return: response
    """
    recipe_permission_check(request, Crud.READ)

    count = 0
    while not count:
        search_term = choice(SEARCH_TERMS)
        recipes = get_recipe_by_category_keyword(
            category_name=search_term, keyword_name=search_term)
        count = recipes.count()

    added_indices = set()

    def pick_index():
        while len(added_indices) < RECIPES_PER_PAGE:
            index = randint(0, count - 1)
            if index not in added_indices:
                added_indices.add(index)
        return list(added_indices)

    indices = [idx for idx in range(count)] \
        if count <= RECIPES_PER_PAGE else pick_index()
    recipe_list = [
        RecipeDto.from_model(recipes[idx]) for idx in indices
    ]

    def carousel_item(r_dto):
        tagline = choice(TAGLINES).format(capwords(search_term))
        return [
            CarouselItem(
                url=static(item.url) if item.static else item.url,
                alt='recipe image', lead=tagline, active=idx == 0
            ) for idx, item in enumerate(r_dto.carousel.urls)
        ]

    carousel_list = [
        carousel_item(r_dto) for r_dto in recipe_list
    ]

    context = {
        TITLE_CTX: 'Recipe Home',
        TAGLINE_CTX: choice(TAGLINES).format(capwords(search_term)),
        RECIPE_LIST_CTX: recipe_list,
        CAROUSEL_LIST_CTX: carousel_list,
    }

    return render(request, app_template_path(THIS_APP, 'recipe_home.html'),
                  context=context)
