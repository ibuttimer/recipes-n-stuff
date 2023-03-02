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
from string import capwords
from typing import TypeVar, Optional, Union

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.templatetags.static import static


from utils import app_template_path
from utils.views import REDIRECT_CTX

from .constants import (
    MODAL_LEVEL_CTX, TITLE_CLASS_CTX, InfoModalLevel, THIS_APP
)

TITLE_CTX = 'title'
MESSAGE_CTX = 'message'
IDENTIFIER_CTX = 'identifier'
SHOW_INFO_CTX = 'show_info'
INFO_TOAST_CTX = 'info_toast'

# workaround for self type hints from https://peps.python.org/pep-0673/
TypeInfoModalTemplate = \
    TypeVar("TypeInfoModalTemplate", bound="InfoModalTemplate")


CAROUSEL_CTX = 'carousel'

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


@dataclass
class CarouselItem:
    """ Class representing a carousel item """
    url: str
    alt: str
    lead: str
    active: bool


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


@dataclass
class InfoModalTemplate:
    """ Info modal template data """
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
        :param info: template info or string
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


def info_toast_payload(message: Union[str, InfoModalTemplate]) -> dict:
    """
    Generate payload for an info toast response.
    :param message: toast message
    :return: payload
    """
    return {
        INFO_TOAST_CTX: InfoModalTemplate.render(message)
    }


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
