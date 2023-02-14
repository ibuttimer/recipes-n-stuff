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

from http import HTTPStatus
from typing import Union

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views import View

from base.utils import raise_permission_denied
from utils import (
    Crud, reverse_q,
    namespaced_url, redirect_on_success_or_render,
    entity_delete_result_payload
)
from .recipe_queries import (
    get_recipe, get_recipe_ingredient, get_recipe_ingredients_list
)
from .utils import recipe_permission_check
from ..constants import (
    THIS_APP, RECIPE_ID_UPDATE_ROUTE_NAME
)
from ..forms import RecipeIngredientForm
from ..models import Recipe, RecipeIngredient


class RecipeIngredientDetail(LoginRequiredMixin, View):
    """
    Class-based view for recipe ingredient update/delete
    """

    def post(self, request: HttpRequest, pk: int,
             *args, **kwargs) -> HttpResponse:
        """
        POST method to update RecipeIngredient
        :param request: http request
        :param pk: id of recipe
        :param args: additional arbitrary arguments
        :param kwargs: additional keyword arguments
        :return: http response
        """
        recipe_permission_check(request, Crud.UPDATE)

        recipe_ingredient, _ = get_recipe_ingredient(pk)

        form = RecipeIngredientForm(
            data=request.POST, instance=recipe_ingredient)

        if form.is_valid():
            # update object
            # django autocommits changes
            # https://docs.djangoproject.com/en/4.1/topics/db/transactions/#autocommit
            form.save()

            check_ingredient_ordering(recipe_ingredient.recipe)

            redirect_to = self.url(recipe_ingredient.recipe.id)
            template_path, context = None, None
        else:
            redirect_to = None
            template_path, context = self.render_info(form)

        return redirect_on_success_or_render(
            request, redirect_to is not None, redirect_to=redirect_to,
            template_path=template_path, context=context)

    # def render_info(self, form: IngredientForm) -> tuple[
    #         str, dict[str, Ingredient | list[str] | IngredientForm | bool]
    # ]:
    #     """
    #     Get info to render a subscription entry
    #     :param form: form to use
    #     :return: tuple of template path and context
    #     """
    #     return for_subscription_form_render(
    #         TITLE_UPDATE, Crud.UPDATE, **{
    #             SUBMIT_URL_CTX: self.url(form.instance.pk),
    #             SUBSCRIPTION_FORM_CTX: IngredientCreate.init_form(form)
    #         })

    def delete(self, request: HttpRequest, pk: int,
               *args, **kwargs) -> HttpResponse:
        """
        DELETE method to delete Ingredient
        :param request: http request
        :param pk: id of address
        :param args: additional arbitrary arguments
        :param kwargs: additional keyword arguments
        :return: http response
        """
        recipe_permission_check(request, Crud.DELETE)

        recipe_ingredient, _ = get_recipe_ingredient(pk)

        own_recipe_check(request, recipe_ingredient.recipe)

        status = HTTPStatus.OK
        # delete ingredient
        count, _ = recipe_ingredient.delete()
        payload = entity_delete_result_payload(
            "#id__ingredient_deleted-modal-body", count > 0, 'ingredient')

        if count == 0:
            status = HTTPStatus.BAD_REQUEST

        return JsonResponse(payload, status=status)

    def url(self, pk: int) -> str:
        """
        Get url for recipe ingredient update/delete
        :param pk: id of entity
        :return: url
        """
        return reverse_q(
            namespaced_url(THIS_APP, RECIPE_ID_UPDATE_ROUTE_NAME),
            args=[pk]
        )


def check_ingredient_ordering(recipe: Union[int, Recipe]):
    """
    Check and update if necessary the recipe ingredients order for the
    specified recipe
    :param recipe: id of recipe or recipe object
    """
    if isinstance(recipe, int):
        recipe = get_recipe(recipe)

    ingredients = get_recipe_ingredients_list(
        recipe, order_by=RecipeIngredient.INDEX_FIELD)

    expected_idx = RecipeIngredient.RECIPE_INGREDIENT_ATTRIB_INDEX_MIN
    alt_end_idx = 0
    for index, ingredient in enumerate(ingredients):
        if index < alt_end_idx:
            continue    # skip alternatives

        assert ingredient.index >= expected_idx
        # alternative ingredients have same index
        alt_end_idx = index
        while alt_end_idx < len(ingredients) and \
                ingredients[alt_end_idx].index == ingredient.index:
            alt_end_idx += 1

        if ingredient.index > expected_idx:
            for alt_idx in range(index, alt_end_idx):
                update_ingredient = ingredients[alt_idx]
                update_ingredient.index = expected_idx
                update_ingredient.save()

        expected_idx += 1


def own_recipe_check(request: HttpRequest, recipe: Recipe,
                     raise_ex: bool = True) -> bool:
    """
    Check request user is recipe owner
    :param request: http request
    :param recipe: recipe
    :param raise_ex: raise exception if not own; default True
    """
    is_own = request.user.id == recipe.author.id
    if not (is_own or request.user.is_superuser) and raise_ex:
        raise_permission_denied(request, recipe, plural='s')

    return is_own
