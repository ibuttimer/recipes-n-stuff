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

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.views.decorators.http import require_http_methods

from utils import (
    Crud, redirect_on_success_or_render,
    POST
)
from . import RecipeDetailUpdate
from .recipe_instruction_by import check_instruction_ordering
from .recipe_queries import get_recipe
from .utils import recipe_permission_check
from ..constants import INSTRUCTIONS_QUERY
from ..forms import RecipeInstructionForm


@login_required
@require_http_methods([POST])
def create_recipe_instruction(request: HttpRequest, pk: int) -> HttpResponse:
    """
    View function to create a recipe instruction
    :param request: http request
    :param pk: id of recipe
    :return: response
    """
    recipe_permission_check(request, Crud.UPDATE)

    recipe, _ = get_recipe(pk)

    form = RecipeInstructionForm(data=request.POST)

    if form.is_valid():
        # save object
        # django autocommits changes
        # https://docs.djangoproject.com/en/4.1/topics/db/transactions/#autocommit
        instruction = form.save()

        recipe.instructions.add(instruction)

        check_instruction_ordering(recipe)

        redirect_to = RecipeDetailUpdate.url(recipe.id, INSTRUCTIONS_QUERY)
        template_path, context = None, None
    else:
        redirect_to = None
        template_path, context = \
            RecipeDetailUpdate.render_update_instructions(
                request, recipe, new_form=form)

    return redirect_on_success_or_render(
        request, redirect_to is not None, redirect_to=redirect_to,
        template_path=template_path, context=context)
