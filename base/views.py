#  MIT License
#
#  Copyright (c) 2022-2023 Ian Buttimer
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
from enum import Enum
from string import capwords
from typing import TypeVar, Optional, Union

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.templatetags.static import static
from django.views.decorators.http import require_GET

from recipes.constants import RECIPE_HOME_ROUTE_NAME
from recipesnstuff import ADMIN_URL, ACCOUNTS_URL, VAL_TEST_PATH_PREFIX
from recipesnstuff.constants import (
    CHECKOUT_URL, ROBOTS_URL, USERS_URL, RECIPES_APP_NAME
)
from utils import app_template_path, namespaced_url
from utils.views import REDIRECT_CTX

from .constants import (
    MODAL_LEVEL_CTX, TITLE_CLASS_CTX, InfoModalLevel, THIS_APP,
    TOAST_POSITION_CTX
)

DISALLOWED_URLS = [
    ADMIN_URL, ACCOUNTS_URL, USERS_URL, CHECKOUT_URL
]

TITLE_CTX = 'title'
MESSAGE_CTX = 'message'
IDENTIFIER_CTX = 'identifier'
SHOW_INFO_CTX = 'show_info'
INFO_TOAST_CTX = 'info_toast'

# workaround for self type hints from https://peps.python.org/pep-0673/
TypeInfoModalTemplate = \
    TypeVar("TypeInfoModalTemplate", bound="InfoModalTemplate")
TypeToastTemplate = \
    TypeVar("TypeToastTemplate", bound="ToastTemplate")


CAROUSEL_CTX = 'carousel'
CAROUSEL_LIST_CTX = 'carousel_list'


@dataclass
class CarouselItem:
    """ Class representing a carousel item """
    url: str
    alt: str
    lead: str
    active: bool


CAROUSEL = [(
    'img/chef-4807317_1920.jpg', 'Oriental chef image',
    'Oriental inspiration', True
    ), (
    'img/meat-skewer-1440105_1920.jpg', 'Barbeque skewers image',
    'Chillin while grilling', False
    ), (
        'img/baked-goods-1846460_1920.jpg', 'Baked goods image',
        'Blueberry bakes', False
    ),
]


@require_GET
def get_landing(request: HttpRequest) -> HttpResponse:
    """
    Render landing page
    :param request: request
    :return: response
    """
    return render(request, app_template_path(THIS_APP, 'landing.html'),
                  context={
                      CAROUSEL_CTX: [
                          CarouselItem(static(url), alt, lead, active)
                          for url, alt, lead, active in CAROUSEL
                      ]
                  })


@require_GET
def get_home(request: HttpRequest) -> HttpResponse:
    """
    Render home page
    :param request: request
    :return: response
    """
    return get_landing(request) \
        if not request.user or not request.user.is_authenticated else \
        redirect(namespaced_url(RECIPES_APP_NAME, RECIPE_HOME_ROUTE_NAME))


@require_GET
def get_help(request: HttpRequest) -> HttpResponse:
    """
    Render help page
    :param request: request
    :return: response
    """
    from recipes.views.utils import duration_help_context

    context = duration_help_context()
    return render(request, app_template_path(THIS_APP, 'help.html'),
                  context=context)


@dataclass(kw_only=True)
class InfoModalTemplate:
    """ Info modal template data """
    # require kw_only to avoid 'non-default argument follows default argument'
    # https://docs.python.org/3.10/library/dataclasses.html#module-contents
    template: str
    context: Optional[dict] = None
    request: Optional[HttpRequest] = None

    def make(self) -> str:
        """
        Render this template
        :return: rendered template or string
        """
        return self.render(self)

    @staticmethod
    def render(info: Union[str, TypeInfoModalTemplate]) -> str:
        """
        Render template
        :param info: modal template or string
        :return: rendered template or string
        """
        return render_to_string(
            info.template, context=info.context, request=info.request
        ) if isinstance(info, InfoModalTemplate) else info


def info_modal_payload(title: Union[str, InfoModalTemplate],
                       message: Union[str, InfoModalTemplate],
                       identifier: str, redirect_url: str = None) -> dict:
    """
    Generate payload for an info modal response.
    :param title: modal title
    :param message: modal message
    :param identifier: unique identifier
    :param redirect_url: url to redirect to when modal closes; default None
    :return: payload
    """
    if not identifier:
        identifier = ''
    return {
        SHOW_INFO_CTX: {
            TITLE_CTX: InfoModalTemplate.render(title),
            MESSAGE_CTX: InfoModalTemplate.render(message),
            REDIRECT_CTX: redirect_url or '',
            IDENTIFIER_CTX: identifier
        }
    }


def render_info_modal_title(level: InfoModalLevel) -> dict:
    """
    Generate an info modal title html.
    :param level: modal title level
    :return: html
    """
    if isinstance(level, InfoModalLevel):
        if level == InfoModalLevel.NONE:
            title = ''
        else:
            modal_cfg = level.value[1]
            title = InfoModalTemplate(
                app_template_path(
                    THIS_APP, "snippet", "info_title.html"),
                context={
                    TITLE_CTX: capwords(modal_cfg.title_text),
                    MODAL_LEVEL_CTX: modal_cfg.name,
                    TITLE_CLASS_CTX: modal_cfg.title_class,
                }
            )
    return InfoModalTemplate.render(title)


def level_info_modal_context(level: InfoModalLevel,
                             message: Union[str, InfoModalTemplate],
                             identifier: str,
                             redirect_url: str = None) -> dict:
    """
    Generate data for an info modal response.
    :param level: modal title level
    :param message: modal message
    :param identifier: unique identifier
    :param redirect_url: url to redirect to when modal closes; default None
    :return: response dict
    """
    return {
        TITLE_CTX: render_info_modal_title(level),
        MESSAGE_CTX: InfoModalTemplate.render(message),
        REDIRECT_CTX: redirect_url or '',
        IDENTIFIER_CTX: identifier
    }


def level_info_modal_payload(level: InfoModalLevel,
                             message: Union[str, InfoModalTemplate],
                             identifier: str,
                             redirect_url: str = None) -> dict:
    """
    Generate an info modal payload.
    :param level: modal title level
    :param message: modal message
    :param identifier: unique identifier
    :param redirect_url: url to redirect to when modal closes; default None
    :return: response dict
    """
    return {
        SHOW_INFO_CTX: level_info_modal_context(
            level, message, identifier, redirect_url=redirect_url)
    }


def render_level_info_modal(level: InfoModalLevel,
                            message: Union[str, InfoModalTemplate],
                            identifier: str,
                            redirect_url: str = None) -> dict:
    """
    Generate an info modal html.
    :param level: modal title level
    :param message: modal message
    :param identifier: unique identifier
    :param redirect_url: url to redirect to when modal closes; default None
    :return: response
    """
    return render_to_string(
        app_template_path(
            THIS_APP, "snippet", "info_modal.html"),
        context=level_info_modal_context(
            level, message, identifier, redirect_url=redirect_url)
    )


class ToastPosition(Enum):
    """
    Enum representing bootstrap toast positions
    https://getbootstrap.com/docs/5.3/components/toasts/#placement
    """
    TOP_LEFT = "top-0 start-0"
    TOP_CENTRE = "top-0 start-50 translate-middle-x"
    TOP_RIGHT = "top-0 end-0"
    MIDDLE_LEFT = "top-50 start-0 translate-middle-y"
    MIDDLE_CENTRE = "top-50 start-50 translate-middle"
    MIDDLE_RIGHT = "top-50 end-0 translate-middle-y"
    BOTTOM_LEFT = "bottom-0 start-0"
    BOTTOM_CENTRE = "bottom-0 start-50 translate-middle-x"
    BOTTOM_RIGHT = "bottom-0 end-0"


ToastPosition.DEFAULT = ToastPosition.TOP_RIGHT


@dataclass(kw_only=True)
class ToastTemplate(InfoModalTemplate):
    """ Toast template data """
    position: ToastPosition = ToastPosition.DEFAULT

    def make(self) -> str:
        """
        Render this template
        :return: rendered template or string
        """
        return self.render(self, position=self.position)

    @staticmethod
    def render(toast: Union[str, TypeToastTemplate],
               position: ToastPosition = ToastPosition.DEFAULT) -> str:
        """
        Render template
        :param toast: toast template or string
        :param position: display position; default ToastPosition.DEFAULT
        :return: rendered template or string
        """
        context = toast.context or {}
        context[TOAST_POSITION_CTX] = position.value
        return render_to_string(
            toast.template, context=context, request=toast.request
        ) if isinstance(toast, ToastTemplate) else toast


def info_toast_payload(
        message: Union[str, ToastTemplate],
        position: ToastPosition = ToastPosition.DEFAULT) -> dict:
    """
    Generate payload for an info toast response.
    :param message: toast message
    :param position: display position; default ToastPosition.DEFAULT
    :return: payload
    """
    return {
        INFO_TOAST_CTX: ToastTemplate.render(message),
        TOAST_POSITION_CTX: position.value
    }


@require_GET
def get_about(request: HttpRequest) -> HttpResponse:
    """
    Render about page
    :param request: request
    :return: response
    """
    context = {}
    # context.update(get_search_terms_help())
    # context.update(get_reactions_help())
    return render(
        request, app_template_path(THIS_APP, "about.html"),
        context=context
    )


@require_GET
def get_privacy(request: HttpRequest) -> HttpResponse:
    """
    Render privacy page
    :param request: request
    :return: response
    """
    return render(
        request, app_template_path(THIS_APP, "privacy.html")
    )


@require_GET
def robots_txt(request):
    """
    View function for robots.txt
    Based on https://adamj.eu/tech/2020/02/10/robots-txt/
    :param request: http request
    :return: robots.txt response
    """
    lines = [
        "User-Agent: *",
        f"Disallow: /{VAL_TEST_PATH_PREFIX}"
    ]
    lines.extend([
        f"Disallow: /{url}" for url in DISALLOWED_URLS
    ])
    lines.extend([
        f"Disallow: /{app_name}/{VAL_TEST_PATH_PREFIX}"
        for app_name in [RECIPES_APP_NAME]
    ])
    lines.append(
        'Sitemap: {}'.format(
            request.build_absolute_uri().replace(ROBOTS_URL, 'sitemap.xml'))
    )
    return HttpResponse("\n".join(lines), content_type="text/plain")
