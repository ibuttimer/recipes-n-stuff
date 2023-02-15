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
from typing import Union, Tuple

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import BadRequest
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views import View

from utils.content_list_mixin import get_query_args
from .dto import RecipeDto
from .recipe_queries import get_recipe, get_recipe_ingredients_list
from ..constants import (
    THIS_APP, INGREDIENTS_CTX, NEW_INGREDIENT_FORM_CTX,
    RECIPE_ID_INGREDIENT_NEW_ROUTE_NAME, RECIPE_ID_UPDATE_ROUTE_NAME,
    REFRESH_URL_CTX, NEW_URL_CTX, INGREDIENTS_QUERY, INSTRUCTIONS_QUERY,
    INSTRUCTIONS_CTX, NEW_INSTRUCTION_FORM_CTX,
    RECIPE_ID_INSTRUCTION_NEW_ROUTE_NAME
)
from utils import (
    Crud, app_template_path, reverse_q,
    namespaced_url, PAGE_HEADING_CTX, TITLE_CTX, QueryOption
)
from .utils import recipe_permission_check
from ..constants import RECIPE_ID_ROUTE_NAME, RECIPE_DTO_CTX
from ..forms import (
    RecipeIngredientForm, RecipeIngredientNewForm, RecipeInstructionForm
)
from ..models import Recipe, Instruction

TITLE_UPDATE = 'Update Recipe'

UPDATE_QUERY_ARGS = [
    QueryOption.of_no_cls_dflt(INGREDIENTS_QUERY),
    QueryOption.of_no_cls_dflt(INSTRUCTIONS_QUERY),
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

        recipe_dto = RecipeDto.from_id(pk)

        return render(
            request, app_template_path(THIS_APP, 'recipe_view.html'),
            context={
                TITLE_CTX: recipe_dto.name,
                RECIPE_DTO_CTX: recipe_dto
            }
        )

    # def post(self, request: HttpRequest, pk: int,
    #          *args, **kwargs) -> HttpResponse:
    #     """
    #     POST method to update Recipe
    #     :param request: http request
    #     :param pk: id of address
    #     :param args: additional arbitrary arguments
    #     :param kwargs: additional keyword arguments
    #     :return: http response
    #     """
    #     subscription_permission_check(request, Crud.UPDATE)
    #
    #     subscription, query_param = get_subscription(pk)
    #
    #     form = RecipeForm(data=request.POST, instance=subscription)
    #
    #     if form.is_valid():
    #         # update object
    #         # django autocommits changes
    #         # https://docs.djangoproject.com/en/4.1/topics/db/transactions/#autocommit
    #         form.save()
    #
    #         redirect_to = reverse_q(
    #             namespaced_url(THIS_APP, SUBSCRIPTIONS_ROUTE_NAME)
    #         )
    #         template_path, context = None, None
    #     else:
    #         redirect_to = None
    #         template_path, context = self.render_info(form)
    #
    #     return redirect_on_success_or_render(
    #         request, redirect_to is not None, redirect_to=redirect_to,
    #         template_path=template_path, context=context)

    # def render_info(self, form: RecipeForm) -> tuple[
    #         str, dict[str, Recipe | list[str] | RecipeForm | bool]
    # ]:
    #     """
    #     Get info to render a subscription entry
    #     :param form: form to use
    #     :return: tuple of template path and context
    #     """
    #     return for_subscription_form_render(
    #         TITLE_UPDATE, Crud.UPDATE, **{
    #             SUBMIT_URL_CTX: self.url(form.instance.pk),
    #             SUBSCRIPTION_FORM_CTX: RecipeCreate.init_form(form)
    #         })
    #
    # def delete(self, request: HttpRequest, pk: int,
    #            *args, **kwargs) -> HttpResponse:
    #     """
    #     DELETE method to delete Recipe
    #     :param request: http request
    #     :param pk: id of address
    #     :param args: additional arbitrary arguments
    #     :param kwargs: additional keyword arguments
    #     :return: http response
    #     """
    #     subscription_permission_check(request, Crud.UPDATE)
    #
    #     address, _ = get_subscription(pk)
    #
    #     # TODO refactor delete modals to single template
    #
    #     status = HTTPStatus.OK
    #     # delete address
    #     count, _ = address.delete()
    #     payload = replace_inner_html_payload(
    #         "#id--subscription-deleted-modal-body",
    #         render_to_string(
    #             app_template_path(
    #                 THIS_APP, "snippet", "subscription_delete.html"),
    #             context={
    #                 STATUS_CTX: count > 0
    #             },
    #             request=request)
    #     )
    #     if count == 0:
    #         status = HTTPStatus.BAD_REQUEST
    #
    #     return JsonResponse(payload, status=status)

    def url(self, pk: int) -> str:
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
        recipe_permission_check(request, Crud.UPDATE)

        query_args = get_query_args(request, UPDATE_QUERY_ARGS)

        for query, field in [
            (INGREDIENTS_QUERY, Recipe.INGREDIENTS_FIELD),
            (INSTRUCTIONS_QUERY, Recipe.INSTRUCTIONS_FIELD),
        ]:
            if query_args[query].was_set_to_boolean_true():
                field_name = field
                break
        else:
            raise BadRequest(f'Malformed request; query not specified')

        if field_name == Recipe.INGREDIENTS_FIELD:
            template, context = self.render_update_ingredients(request, pk)
        else:
            template, context = self.render_update_instructions(request, pk)

        return render(request, template, context=context)

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
                ingredients[-1].index + 1

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
                instructions[-1].index + 1

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

    # def post(self, request: HttpRequest, pk: int,
    #          *args, **kwargs) -> HttpResponse:
    #     """
    #     POST method to update Recipe
    #     :param request: http request
    #     :param pk: id of address
    #     :param args: additional arbitrary arguments
    #     :param kwargs: additional keyword arguments
    #     :return: http response
    #     """
    #     subscription_permission_check(request, Crud.UPDATE)
    #
    #     subscription, query_param = get_subscription(pk)
    #
    #     form = RecipeForm(data=request.POST, instance=subscription)
    #
    #     if form.is_valid():
    #         # update object
    #         # django autocommits changes
    #         # https://docs.djangoproject.com/en/4.1/topics/db/transactions/#autocommit
    #         form.save()
    #
    #         redirect_to = reverse_q(
    #             namespaced_url(THIS_APP, SUBSCRIPTIONS_ROUTE_NAME)
    #         )
    #         template_path, context = None, None
    #     else:
    #         redirect_to = None
    #         template_path, context = self.render_info(form)
    #
    #     return redirect_on_success_or_render(
    #         request, redirect_to is not None, redirect_to=redirect_to,
    #         template_path=template_path, context=context)

    # def render_info(self, form: RecipeForm) -> tuple[
    #         str, dict[str, Recipe | list[str] | RecipeForm | bool]
    # ]:
    #     """
    #     Get info to render a subscription entry
    #     :param form: form to use
    #     :return: tuple of template path and context
    #     """
    #     return for_subscription_form_render(
    #         TITLE_UPDATE, Crud.UPDATE, **{
    #             SUBMIT_URL_CTX: self.url(form.instance.pk),
    #             SUBSCRIPTION_FORM_CTX: RecipeCreate.init_form(form)
    #         })
    #
    # def delete(self, request: HttpRequest, pk: int,
    #            *args, **kwargs) -> HttpResponse:
    #     """
    #     DELETE method to delete Recipe
    #     :param request: http request
    #     :param pk: id of address
    #     :param args: additional arbitrary arguments
    #     :param kwargs: additional keyword arguments
    #     :return: http response
    #     """
    #     subscription_permission_check(request, Crud.UPDATE)
    #
    #     address, _ = get_subscription(pk)
    #
    #     # TODO refactor delete modals to single template
    #
    #     status = HTTPStatus.OK
    #     # delete address
    #     count, _ = address.delete()
    #     payload = replace_inner_html_payload(
    #         "#id--subscription-deleted-modal-body",
    #         render_to_string(
    #             app_template_path(
    #                 THIS_APP, "snippet", "subscription_delete.html"),
    #             context={
    #                 STATUS_CTX: count > 0
    #             },
    #             request=request)
    #     )
    #     if count == 0:
    #         status = HTTPStatus.BAD_REQUEST
    #
    #     return JsonResponse(payload, status=status)

    @staticmethod
    def url(pk: int, query: str) -> str:
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
            }
        )
