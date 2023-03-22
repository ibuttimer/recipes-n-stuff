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

from base.templatetags.delete_modal_ids import delete_modal_ids
from utils import (
    Crud, redirect_on_success_or_render, entity_delete_result_payload
)
from .recipe_by import RecipeDetailUpdate
from .ingredient_by import check_ordering
from .recipe_queries import (
    get_recipe, get_recipe_instruction, own_recipe_check
)
from .utils import recipe_permission_check
from ..constants import (
    INSTRUCTIONS_QUERY
)
from ..forms import RecipeInstructionForm
from ..models import Recipe, Instruction


class InstructionDetail(LoginRequiredMixin, View):
    """
    Class-based view for recipe ingredient update/delete
    """

    def post(self, request: HttpRequest, pk: int,
             *args, **kwargs) -> HttpResponse:
        """
        POST method to update Instruction
        :param request: http request
        :param pk: id of recipe
        :param args: additional arbitrary arguments
        :param kwargs: additional keyword arguments
        :return: http response
        """
        recipe_permission_check(request, Crud.UPDATE)

        instruction, _ = get_recipe_instruction(pk)

        # TODO instruction should be a many-to-one relationship with recipe
        recipe = self.get_recipe(instruction)
        own_recipe_check(request, recipe)

        form = RecipeInstructionForm(
            data=request.POST, instance=instruction)

        if form.is_valid():
            # update object
            # django autocommits changes
            # https://docs.djangoproject.com/en/4.1/topics/db/transactions/#autocommit
            form.save()

            check_instruction_ordering(recipe)

            redirect_to = self.url(recipe.id)
            template_path, context = None, None
        else:
            # TODO
            redirect_to = None
            template_path, context = self.render_info(form)

        return redirect_on_success_or_render(
            request, redirect_to is not None, redirect_to=redirect_to,
            template_path=template_path, context=context)

    def get_recipe(self, instruction: Instruction):
        """ Get the recipe for the specified instruction"""
        # TODO instruction should be a many-to-one relationship with recipe
        return list(instruction.recipe_set.all())[0]

    def delete(self, request: HttpRequest, pk: int,
               *args, **kwargs) -> HttpResponse:
        """
        DELETE method to delete Instruction
        :param request: http request
        :param pk: id of address
        :param args: additional arbitrary arguments
        :param kwargs: additional keyword arguments
        :return: http response
        """
        recipe_permission_check(request, Crud.DELETE)

        instruction, _ = get_recipe_instruction(pk)

        recipe = self.get_recipe(instruction)
        own_recipe_check(request, recipe)

        status = HTTPStatus.OK
        # delete instruction
        count, _ = instruction.delete()

        entity = 'instruction'
        modal_ids = delete_modal_ids(entity)
        payload = entity_delete_result_payload(
            f"#{modal_ids['deleted_id_body']}", count > 0, entity)

        if count == 0:
            status = HTTPStatus.BAD_REQUEST

        return JsonResponse(payload, status=status)

    def url(self, pk: int) -> str:
        """
        Get url for recipe instruction update/delete
        :param pk: id of entity
        :return: url
        """
        return RecipeDetailUpdate.url(pk, INSTRUCTIONS_QUERY)


def check_instruction_ordering(recipe: Union[int, Recipe]):
    """
    Check and update if necessary the recipe instructions order for the
    specified recipe
    :param recipe: id of recipe or recipe object
    """
    if isinstance(recipe, int):
        recipe = get_recipe(recipe)

    instructions = list(
        recipe.instructions.order_by(Instruction.INDEX_FIELD).all())

    check_ordering(instructions, Instruction.INDEX_FIELD,
                   start=Instruction.INSTRUCTION_ATTRIB_INDEX_MIN)
