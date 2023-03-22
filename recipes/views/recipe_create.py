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

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views import View

from base.constants import SUBMIT_BTN_TEXT
from recipesnstuff import DEV_IMAGE_FILE_TYPES, IMAGE_FILE_TYPES
from recipesnstuff.settings import RECIPE_BLANK_URL, DEVELOPMENT
from utils import (
    Crud, READ_ONLY_CTX, SUBMIT_URL_CTX, app_template_path, reverse_q,
    namespaced_url, TITLE_CTX, redirect_on_success_or_render,
    PAGE_HEADING_CTX, SUBMIT_BTN_TEXT_CTX
)

from recipes.constants import (
    THIS_APP, RECIPE_NEW_ROUTE_NAME,
    RECIPE_FORM_CTX, RECIPE_FORM_RHS_FIELDS_CTX,
    RECIPE_URL_CTX, IMAGE_FILE_TYPES_CTX, CATEGORY_LIST_CTX,
    RECIPE_ID_ROUTE_NAME
)
from recipes.forms import RecipeForm
from recipes.models import Recipe, Category
from .dto import RecipeDto

from .utils import recipe_permission_check

TITLE_NEW = 'Create Recipe'


class RecipeCreate(LoginRequiredMixin, View):
    """
    Class-based view for recipe creation
    """

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """
        GET method for Recipe
        :param request: http request
        :param args: additional arbitrary arguments
        :param kwargs: additional keyword arguments
        :return: http response
        """
        recipe_permission_check(request, Crud.CREATE)

        template_path, context = self.render_info(RecipeForm())

        return render(request, template_path, context=context)

    @staticmethod
    def init_form(form: RecipeForm):
        """ Initialise form display """
        for field in [
            Recipe.NAME_FIELD, Recipe.DESCRIPTION_FIELD
        ]:
            if field not in form.initial:
                form.initial[field] = ""
        return form

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """
        POST method to create Recipe
        :param request: http request
        :param args: additional arbitrary arguments
        :param kwargs: additional keyword arguments
        :return: http response
        """
        recipe_permission_check(request, Crud.CREATE)

        form = RecipeForm(data=request.POST, files=request.FILES)
        form.full_clean()

        if form.is_valid():
            # save new object
            form.instance.author = request.user

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
            template_path, context = self.render_info(form)

        return redirect_on_success_or_render(
            request, redirect_to is not None, redirect_to=redirect_to,
            template_path=template_path, context=context)

    def render_info(self, form: RecipeForm):
        """
        Get info to render a recipe form
        :param form: form to use
        :return: tuple of template path and context
        """
        return for_recipe_form_render(
            TITLE_NEW, Crud.CREATE, **{
                SUBMIT_URL_CTX: self.url(),
                RECIPE_FORM_CTX: form
            })

    def url(self) -> str:
        """
        Get url for address creation
        :return: url
        """
        return reverse_q(
            namespaced_url(THIS_APP, RECIPE_NEW_ROUTE_NAME)
        )


def for_recipe_form_render(
        title: str, action: Crud, **kwargs: object
) -> tuple[str, dict[str, Recipe | list[str] | RecipeForm | bool]]:
    """
    Get the template and context to Render the recipe template
    :param title: title
    :param action: form action
    :param kwargs: context keyword values, see get_opinion_context()
    :return: tuple of template path and context
    """
    context = {
        TITLE_CTX: title,
        PAGE_HEADING_CTX: title,
        SUBMIT_BTN_TEXT_CTX: SUBMIT_BTN_TEXT[action],
        READ_ONLY_CTX: kwargs.get(READ_ONLY_CTX, False),
    }

    context_form = kwargs.get(RECIPE_FORM_CTX, None)
    if context_form:
        # image to display
        initial = context_form.initial.get(RecipeForm.PICTURE_FF, None)
        initial = None if RecipeDto.has_no_uploaded_picture(initial) \
            else initial.url
        recipe_url = initial or RECIPE_BLANK_URL

        context.update({
            RECIPE_FORM_CTX: context_form,
            RECIPE_FORM_RHS_FIELDS_CTX: [
                RecipeForm.NAME_FF, RecipeForm.PREP_TIME_FF,
                RecipeForm.COOK_TIME_FF, RecipeForm.SERVINGS_FF,
                RecipeForm.CATEGORY_FF, RecipeForm.YIELD_FF
            ],
            RECIPE_URL_CTX: recipe_url,
            # not all image types are supported by Pillow which is used by
            # ImageField in dev mode
            IMAGE_FILE_TYPES_CTX:
                DEV_IMAGE_FILE_TYPES if DEVELOPMENT else IMAGE_FILE_TYPES,
            CATEGORY_LIST_CTX: list(
                map(lambda category: category.name,
                    Category.objects.order_by(Category.NAME_FIELD).all())
            ),
            SUBMIT_URL_CTX: kwargs.get(SUBMIT_URL_CTX, None)
        })

    return app_template_path(THIS_APP, "recipe_form.html"), context


def handle_image(form: RecipeForm, recipe: Recipe):
    """
    Handle image during recipe save
    :param form: recipe form
    :param recipe: recipe instance to save
    """
    # special handing for image
    save_data = form.cleaned_data[RecipeForm.PICTURE_FF]
    if save_data is not None:
        setattr(recipe, RecipeForm.PICTURE_FF, save_data)
