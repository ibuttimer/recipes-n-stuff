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
from dataclasses import dataclass
from http import HTTPStatus
from random import choice
from typing import Union, Tuple, TypeVar

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import BadRequest
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render
from django.views import View
from django.views.decorators.http import require_http_methods

from base.entity_conv import unescape_entities
from base.templatetags.delete_modal_ids import delete_modal_ids
from checkout.basket import add_ingredient_box_to_basket
from order.views.utils import order_permission_check
from utils.content_list_mixin import get_query_args, SUBMIT_URL_CTX
from .dto import RecipeDto
from .recipe_create import for_recipe_form_render, handle_image
from .recipe_queries import (
    get_recipe, get_recipe_ingredients_list, get_recipe_box_product,
    get_recipe_count, nutritional_info_valid, chk_permission_get_recipe
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
    RECIPE_FORM_CTX, INGREDIENT_ID_MAP_CTX, RECIPES_ROUTE_NAME, CALL_TO_BUY_CTX
)
from utils import (
    Crud, app_template_path, reverse_q,
    namespaced_url, PAGE_HEADING_CTX, TITLE_CTX, QueryOption, PATCH,
    redirect_payload, redirect_on_success_or_render,
    entity_delete_result_payload
)
from .utils import recipe_permission_check, encode_timedelta
from ..constants import RECIPE_ID_ROUTE_NAME, RECIPE_DTO_CTX
from ..forms import (
    RecipeIngredientForm, RecipeIngredientNewForm, RecipeInstructionForm,
    RecipeForm
)
from ..models import Recipe, Instruction, Ingredient

TITLE_UPDATE = 'Update Recipe'

UPDATE_QUERY_ARGS = [
    QueryOption.of_no_cls_dflt(INGREDIENTS_QUERY),
    QueryOption.of_no_cls_dflt(INSTRUCTIONS_QUERY),
    QueryOption.of_no_cls_dflt(RECIPE_QUERY),
]

MAX_PRESET_BOX_COUNT = 10
CUSTOM_BOX_COUNT = MAX_PRESET_BOX_COUNT + 1
BOX_COUNT_OPTIONS = [
    (cnt, 'Count' if cnt == 0 else 'Custom'
        if cnt == CUSTOM_BOX_COUNT else f'{cnt}')
    for cnt in range(CUSTOM_BOX_COUNT + 1)
]

TypeRedirectNext = TypeVar("TypeRedirectNext", bound="RedirectNext")

CALL_TO_BUY = [
    'Like the look of this? Save yourself a trip to the shops and purchase '
    'ingredient boxes here!',
    'Take the hassle out of catering a party, ingredient boxes delivered to '
    'your door.',
    "Feeding 1 or 50? We've got you covered. Just a few clicks and your "
    "ingredient boxes are on the way.",
]

class RecipeDetail(LoginRequiredMixin, View):
    """
    Class-based view for recipe get/update/delete
    """

    def get(self, request: HttpRequest, pk: int,
            *args, **kwargs) -> HttpResponse:
        """
        GET method for Recipe
        :param request: http request
        :param pk: id of address
        :param args: additional arbitrary arguments
        :param kwargs: additional keyword arguments
        :return: http response
        """
        recipe_permission_check(request, Crud.READ)

        recipe_dto = RecipeDto.from_id(pk, nutri_text=True)

        box_product, currency = get_recipe_box_product(pk, get_or_404=False)

        is_own = recipe_dto.author == request.user
        can_purchase = box_product is not None
        can_delete = is_own or recipe_permission_check(
            request, Crud.DELETE, raise_ex=False)

        context = {
            TITLE_CTX: recipe_dto.name,
            RECIPE_DTO_CTX: recipe_dto,
            RECIPE_COUNT_CTX: get_recipe_count(recipe_dto.author.username),
            CAN_PURCHASE_CTX: can_purchase,
            IS_OWN_CTX: is_own,
            NUTRITIONAL_INFO_CTX: nutritional_info_valid(recipe_dto.id),
        }
        if can_purchase:
            context.update({
                COUNT_OPTIONS_CTX: BOX_COUNT_OPTIONS,
                SELECTED_COUNT_CTX: 0,
                CUSTOM_COUNT_CTX: CUSTOM_BOX_COUNT,
                CCY_SYMBOL_CTX: currency.symbol,
                UNIT_PRICE_CTX: box_product.unit_price,
                CALL_TO_BUY_CTX: choice(CALL_TO_BUY)
            })
        if can_delete:
            context.update({
                REFRESH_URL_CTX: reverse_q(
                    namespaced_url(THIS_APP, RECIPES_ROUTE_NAME)
                )
            })

        return render(
            request, app_template_path(THIS_APP, 'recipe_view.html'),
            context=context
        )

    def delete(self, request: HttpRequest, pk: int,
               *args, **kwargs) -> HttpResponse:
        """
        DELETE method to delete Recipe
        :param request: http request
        :param pk: id of address
        :param args: additional arbitrary arguments
        :param kwargs: additional keyword arguments
        :return: http response
        """
        recipe = chk_permission_get_recipe(request, pk, Crud.DELETE)

        status = HTTPStatus.OK
        # delete recipe
        count, _ = recipe.delete()
        if count == 0:
            status = HTTPStatus.BAD_REQUEST

        entity = 'recipe'
        ids = delete_modal_ids(entity)
        payload = entity_delete_result_payload(
            f"#{ids['deleted_id_body']}", count > 0, entity)

        return JsonResponse(payload, status=status)

    @staticmethod
    def url(pk: int) -> str:
        """
        Get url for address update/delete
        :param pk: id of entity
        :return: url
        """
        return reverse_q(
            namespaced_url(THIS_APP, RECIPE_ID_ROUTE_NAME),
            args=[pk]
        )


@dataclass
class IngredientInfo:
    """ Data class of ingredient info for editing """
    form: RecipeIngredientForm
    name: str
    measure: str


@dataclass
class InstructionInfo:
    """ Data class of instruction info for editing """
    form: RecipeInstructionForm


class RecipeDetailUpdate(LoginRequiredMixin, View):
    """
    Class-based view for recipe get/update/delete
    """

    def get(self, request: HttpRequest, pk: int,
            *args, **kwargs) -> HttpResponse:
        """
        GET method for Recipe
        :param request: http request
        :param pk: id of recipe
        :param args: additional arbitrary arguments
        :param kwargs: additional keyword arguments
        :return: http response
        """
        recipe = chk_permission_get_recipe(request, pk, Crud.UPDATE)

        query_args = get_query_args(request, UPDATE_QUERY_ARGS)

        for query in [
            INGREDIENTS_QUERY, INSTRUCTIONS_QUERY, RECIPE_QUERY
        ]:
            if query_args[query].was_set_to_boolean_true():
                field_name = query
                break
        else:
            raise BadRequest('Malformed request; query not specified')

        if field_name == INGREDIENTS_QUERY:
            template, context = self.render_update_ingredients(request, pk)
        elif field_name == INSTRUCTIONS_QUERY:
            template, context = self.render_update_instructions(request, pk)
        else:
            form = RecipeForm(instance=recipe)

            form.initial[RecipeForm.PREP_TIME_FF] = \
                encode_timedelta(recipe.prep_time)
            form.initial[RecipeForm.COOK_TIME_FF] = \
                encode_timedelta(recipe.cook_time)
            form.initial[RecipeForm.CATEGORY_FF] = recipe.category.name

            template, context = self.render_info(form, pk)

        return render(request, template, context=context)

    def render_info(self, form: RecipeForm, pk: int, query: str = None):
        """
        Get info to render a recipe form
        :param form: form to use
        :param pk: id of recipe
        :param query: query field
        :return: tuple of template path and context
        """
        return for_recipe_form_render(
            TITLE_UPDATE, Crud.UPDATE, **{
                SUBMIT_URL_CTX: self.url(pk, query),
                RECIPE_FORM_CTX: form
            })

    def post(self, request: HttpRequest, pk: int,
             *args, **kwargs) -> HttpResponse:
        """
        POST method for Recipe
        :param request: http request
        :param pk: id of recipe
        :param args: additional arbitrary arguments
        :param kwargs: additional keyword arguments
        :return: http response
        """
        recipe = chk_permission_get_recipe(request, pk, Crud.UPDATE)

        form = RecipeForm(
            data=request.POST, files=request.FILES, instance=recipe)
        form.full_clean()

        if form.is_valid():
            # update object
            handle_image(form, form.instance)

            recipe = form.save()
            # django autocommits changes
            # https://docs.djangoproject.com/en/4.1/topics/db/transactions/#autocommit

            redirect_to = reverse_q(
                namespaced_url(THIS_APP, RECIPE_ID_ROUTE_NAME),
                args=[recipe.id]
            )
            template_path, context = None, None
        else:
            redirect_to = None
            template_path, context = self.render_info(form, pk)

        return redirect_on_success_or_render(
            request, redirect_to is not None, redirect_to=redirect_to,
            template_path=template_path, context=context)

    @staticmethod
    def render_update_ingredients(
            request: HttpRequest, recipe: Union[int, Recipe],
            new_form: RecipeIngredientNewForm = None) -> Tuple[str, dict]:
        """
        Get the template & context for a recipe ingredients update
        :param request: http request
        :param recipe: id of recipe or recipe object
        :param new_form: form to add new entity; default None
        :return: tuple of template and context
        """
        recipe_permission_check(request, Crud.UPDATE)

        if isinstance(recipe, int):
            recipe, _ = get_recipe(recipe, related=Recipe.INGREDIENTS_FIELD)

        ingredients = get_recipe_ingredients_list(recipe)

        if not new_form:
            new_form = RecipeIngredientNewForm()
            new_form.initial[RecipeIngredientForm.INDEX_FF] = \
                ingredients[-1].index + 1 if len(ingredients) else 1

        context = {
            TITLE_CTX: 'Update Ingredients',
            PAGE_HEADING_CTX: f'Update {recipe.name} Ingredients',
            INGREDIENTS_CTX: list(
                map(lambda entity: IngredientInfo(
                    form=RecipeIngredientForm(instance=entity),
                    name=entity.ingredient.name,
                    measure=entity.ingredient.measure.name),
                    ingredients)
            ),
            NEW_INGREDIENT_FORM_CTX: new_form,
            INGREDIENT_LIST_CTX: list(
                map(lambda ingred: ingred.name,
                    Ingredient.objects.order_by(Ingredient.NAME_FIELD).all())
            ),
            # Due to mixed html entity encoding on ingredient names from the
            # kaggle dataset, can't look up ingredient by name, so provide a
            # map with unescaped name as the key and id as the value, so id
            # may be used as the returned value
            INGREDIENT_ID_MAP_CTX: {
                iname: ikey for iname, ikey in map(
                    lambda ingred: (unescape_entities(ingred.name), ingred.id),
                    Ingredient.objects.order_by(Ingredient.NAME_FIELD).all())
            },
            NEW_URL_CTX: reverse_q(
                namespaced_url(THIS_APP, RECIPE_ID_INGREDIENT_NEW_ROUTE_NAME),
                args=[recipe.id]
            ),
            REFRESH_URL_CTX: RecipeDetailUpdate.url(
                recipe.id, INGREDIENTS_QUERY),
            RECIPE_DTO_CTX: RecipeDto.from_model(recipe, all_attrib=False)
        }

        return app_template_path(THIS_APP, 'ingredients_form.html'), context

    @staticmethod
    def render_update_instructions(
            request: HttpRequest, recipe: Union[int, Recipe],
            new_form: RecipeInstructionForm = None) -> Tuple[str, dict]:
        """
        Get the template & context for a recipe instructions update
        :param request: http request
        :param recipe: id of recipe or recipe object
        :param new_form: form to add new entity; default None
        :return: tuple of template and context
        """
        recipe_permission_check(request, Crud.UPDATE)

        if isinstance(recipe, int):
            recipe, _ = get_recipe(recipe)

        instructions = list(
            recipe.instructions.order_by(Instruction.INDEX_FIELD).all())

        if not new_form:
            new_form = RecipeInstructionForm()
            new_form.initial[RecipeInstructionForm.INDEX_FF] = \
                instructions[-1].index + 1 if len(instructions) else 1

        context = {
            TITLE_CTX: 'Update Instructions',
            PAGE_HEADING_CTX: f'Update {recipe.name} Instructions',
            INSTRUCTIONS_CTX: list(
                map(lambda entity: InstructionInfo(
                    form=RecipeInstructionForm(instance=entity)
                ), instructions)
            ),
            NEW_INSTRUCTION_FORM_CTX: new_form,
            NEW_URL_CTX: reverse_q(
                namespaced_url(
                    THIS_APP, RECIPE_ID_INSTRUCTION_NEW_ROUTE_NAME),
                args=[recipe.id]
            ),
            REFRESH_URL_CTX: RecipeDetailUpdate.url(
                recipe.id, INSTRUCTIONS_QUERY),
            RECIPE_DTO_CTX: RecipeDto.from_model(recipe, all_attrib=False)
        }

        return app_template_path(THIS_APP, 'instructions_form.html'), context

    @staticmethod
    def url(pk: int, query: str = None) -> str:
        """
        Get url for address update/delete
        :param pk: id of entity
        :param query: query field
        :return: url
        """
        return reverse_q(
            namespaced_url(THIS_APP, RECIPE_ID_UPDATE_ROUTE_NAME),
            args=[pk], query_kwargs={
                query: 'y'
            } if query else None
        )


@login_required
@require_http_methods([PATCH])
def add_recipe_to_basket(request: HttpRequest, pk: int) -> HttpResponse:
    """
    View function to add an ingredient box to the basket
    :param request: http request
    :param pk: id of recipe
    :return: response
    """
    recipe_permission_check(request, Crud.READ)
    order_permission_check(request, Crud.CREATE)

    recipe, _ = get_recipe(pk)

    redirect = request.GET.get(NEXT_QUERY, None)

    count = 1
    if QUANTITY_FIELD in request.GET:
        count = int(request.GET[QUANTITY_FIELD])

    payload = add_ingredient_box_to_basket(request, recipe, count=count)
    if redirect:
        payload.update(redirect_payload(
            redirect
        ))

    return JsonResponse(
        payload, status=HTTPStatus.OK if payload else HTTPStatus.BAD_REQUEST)
