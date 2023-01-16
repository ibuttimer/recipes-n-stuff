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
#
from typing import Optional

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.urls import ResolverMatch, resolve, Resolver404

REDIRECT_CTX = "redirect"                   # redirect url
REWRITES_PROP_CTX = 'rewrites'              # multiple html rewrites
ELEMENT_SELECTOR_CTX = 'element_selector'   # element jquery selector
HTML_CTX = 'html'                           # html for rewrite
INNER_HTML_CTX = 'inner_html'               # inner html for rewrite


def redirect_on_success_or_render(request: HttpRequest, success: bool,
                                  redirect_to: str = '/',
                                  *args,
                                  template_path: str = None,
                                  context: dict = None) -> HttpResponse:
    """
    Redirect if success, otherwise render the specified template.
    :param request:         http request
    :param success:         success flag
    :param redirect_to:     a view name that can be resolved by
                            `urls.reverse()` or a URL
    :param args:            optional args for view name, (`urls.reverse()`
                            used to reverse-resolve the name)
    :param template_path:   template to render
    :param context:         context for template
    :return: http response
    """
    response: HttpResponse
    if success:
        # success, redirect
        response = redirect(redirect_to, *args)
    else:
        # render template
        response = render(request, template_path, context=context)
    return response


def resolve_req(
        request: HttpRequest, query: str = None) -> Optional[ResolverMatch]:
    """
    Resolve a request, or a request query parameter
    :param request: http request
    :param query: optional query parameter to resolve
    :return: resolver match or None
    """
    match = None
    path = None
    if query and query in request.GET:
        path = request.GET[query].lower()
    else:
        path = request.path

    if path:
        try:
            match = resolve(path)
        except Resolver404:
            pass    # unable to resolve

    return match


def redirect_payload(url: str, extra: Optional[dict] = None) -> dict:
    """
    Generate payload for a redirect response.
    :param url: url to redirect to
    :param extra: extra payload content; default None
    :return: response
    """
    payload = {
        REDIRECT_CTX: url
    }
    if isinstance(extra, dict):
        payload.update(extra)

    return payload


def _html_payload(selector: str, html: str, key: str,
                  extra: Optional[dict] = None) -> dict:
    """
    Generate payload for a replace html response.
    :param selector: element jquery selector
    :param html: replacement html
    :param extra: extra payload content; default None
    :return: response
    """
    payload = {
        ELEMENT_SELECTOR_CTX: selector,
        key: html
    }
    if isinstance(extra, dict):
        payload.update(extra)

    return payload


def replace_html_payload(selector: str, html: str,
                         extra: Optional[dict] = None) -> dict:
    """
    Generate payload for a replace html response.
    :param selector: element jquery selector
    :param html: replacement html
    :param extra: extra payload content; default None
    :return: response
    """
    return _html_payload(selector, html, HTML_CTX, extra=extra)


def replace_inner_html_payload(selector: str, html: str,
                               extra: Optional[dict] = None) -> dict:
    """
    Generate payload for a replace inner html response.
    :param selector: element jquery selector
    :param html: replacement html
    :param extra: extra payload content; default None
    :return: response
    """
    return _html_payload(selector, html, INNER_HTML_CTX, extra=extra)


def rewrite_payload(*args, extra: Optional[dict] = None) -> dict:
    """
    Generate payload for a rewrite html response.
    :param args: replace html payloads
    :param extra: extra payload content; default None
    :return: response
    """
    payload = {
        REWRITES_PROP_CTX: [*args]
    }
    if isinstance(extra, dict):
        payload.update(extra)

    return payload
