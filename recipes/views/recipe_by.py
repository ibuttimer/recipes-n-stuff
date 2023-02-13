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
from typing import Union, Tuple

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views import View

from .dto import RecipeDto
from .recipe_queries import get_recipe, get_recipe_ingredients_list
from ..constants import (
    THIS_APP, INGREDIENTS_CTX, INGREDIENT_FORM_CTX, INGREDIENT_NAME_CTX,
    MEASURE_NAME_CTX, NEW_INGREDIENT_FORM_CTX,
    RECIPE_ID_INGREDIENT_NEW_ROUTE_NAME, RECIPE_ID_UPDATE_ROUTE_NAME,
    REFRESH_URL_CTX, NEW_URL_CTX
)
from utils import (
    Crud, SUBMIT_URL_CTX, app_template_path, reverse_q,
    namespaced_url, PAGE_HEADING_CTX, TITLE_CTX
)
from .utils import recipe_permission_check
from ..constants import RECIPE_ID_ROUTE_NAME, RECIPE_DTO_CTX
from ..forms import RecipeIngredientForm, RecipeIngredientNewForm
from ..models import Recipe, RecipeIngredient

TITLE_UPDATE = 'Update Recipe'


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
        recipe_permission_check(request, Crud.READ)

        template, context = self.render_update_info(request, pk)

        return render(request, template, context=context)

    @staticmethod
    def render_update_info(
            request: HttpRequest, recipe: Union[int, Recipe],
            new_form: RecipeIngredientNewForm = None) -> Tuple[str, dict]:
        """
        Get the template & context for a recipe ingredients update
        :param request: http request
        :param recipe: id of recipe or recipe object
        :param new_form:
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
                map(lambda ingredient: {
                    INGREDIENT_FORM_CTX: RecipeIngredientForm(
                        instance=ingredient),
                    INGREDIENT_NAME_CTX: ingredient.ingredient.name,
                    MEASURE_NAME_CTX: ingredient.ingredient.measure.name
                }, ingredients)
            ),
            NEW_INGREDIENT_FORM_CTX: new_form,
            NEW_URL_CTX: reverse_q(
                namespaced_url(THIS_APP, RECIPE_ID_INGREDIENT_NEW_ROUTE_NAME),
                args=[recipe.id]
            ),
            REFRESH_URL_CTX: reverse_q(
                namespaced_url(THIS_APP, RECIPE_ID_UPDATE_ROUTE_NAME),
                args=[recipe.id]
            ),
            RECIPE_DTO_CTX: RecipeDto.from_model(recipe, all_attrib=False)
        }

        return app_template_path(THIS_APP, 'ingredients_form.html'), context

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
    def url(pk: int) -> str:
        """
        Get url for address update/delete
        :param pk: id of entity
        :return: url
        """
        return reverse_q(
            namespaced_url(THIS_APP, RECIPE_ID_UPDATE_ROUTE_NAME),
            args=[pk]
        )
