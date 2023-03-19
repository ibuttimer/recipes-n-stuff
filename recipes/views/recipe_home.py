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
from dataclasses import dataclass
from http import HTTPStatus
from string import capwords
from typing import Union, Tuple, TypeVar

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import BadRequest
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render
from django.templatetags.static import static
from django.views import View
from django.views.decorators.http import require_http_methods

from base.entity_conv import unescape_entities
from base.templatetags.delete_modal_ids import delete_modal_ids
from base.views import CAROUSEL_CTX, CarouselItem, CAROUSEL_LIST_CTX
from checkout.basket import add_ingredient_box_to_basket
from order.views.utils import order_permission_check
from utils.content_list_mixin import get_query_args, SUBMIT_URL_CTX
from .dto import RecipeDto
from .recipe_create import for_recipe_form_render, handle_image
from .recipe_queries import (
    get_recipe, get_recipe_ingredients_list, get_recipe_box_product,
    get_recipe_count, nutritional_info_valid, chk_permission_get_recipe,
    get_recipe_by_category_keyword
)
from ..constants import (
    THIS_APP, INGREDIENTS_CTX, NEW_INGREDIENT_FORM_CTX,
    RECIPE_ID_INGREDIENT_NEW_ROUTE_NAME, RECIPE_ID_UPDATE_ROUTE_NAME,
    REFRESH_URL_CTX, NEW_URL_CTX, INGREDIENTS_QUERY, INSTRUCTIONS_QUERY,
    INSTRUCTIONS_CTX, NEW_INSTRUCTION_FORM_CTX,
    RECIPE_ID_INSTRUCTION_NEW_ROUTE_NAME, COUNT_OPTIONS_CTX,
    SELECTED_COUNT_CTX, CUSTOM_COUNT_CTX, CCY_SYMBOL_CTX, UNIT_PRICE_CTX,
    QUANTITY_FIELD, NEXT_QUERY, INGREDIENT_LIST_CTX, RECIPE_COUNT_CTX,
    CAN_PURCHASE_CTX, IS_OWN_CTX, NUTRITIONAL_INFO_CTX, RECIPE_QUERY,
    RECIPE_FORM_CTX, INGREDIENT_ID_MAP_CTX, RECIPES_ROUTE_NAME, TAGLINE_CTX,
    RECIPE_LIST_CTX
)
from utils import (
    Crud, app_template_path, reverse_q,
    namespaced_url, PAGE_HEADING_CTX, TITLE_CTX, QueryOption, PATCH,
    redirect_payload, redirect_on_success_or_render,
    entity_delete_result_payload, GET
)
from .utils import recipe_permission_check, encode_timedelta
from ..constants import RECIPE_ID_ROUTE_NAME, RECIPE_DTO_CTX
from ..forms import (
    RecipeIngredientForm, RecipeIngredientNewForm, RecipeInstructionForm,
    RecipeForm
)
from ..models import Recipe, Instruction, Ingredient

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

    indices = [idx for idx in range(count)] if count <= RECIPES_PER_PAGE else [
        randint(0, count - 1) for _ in range(RECIPES_PER_PAGE)
    ]
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
