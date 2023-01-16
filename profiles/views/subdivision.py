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

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_http_methods

from profiles.models import CountryInfo, Address
from profiles.views.utils import address_permission_check
from utils import GET, Crud, form_auto_id, replace_inner_html_payload


@login_required
@require_http_methods([GET])
def subdivision_name(request: HttpRequest, country: str) -> HttpResponse:
    """
    View function retrieve subdivision name.
    :param request: http request
    :param country: ISO 3166-1 alpha-2 country code
    :return: response
    """
    address_permission_check(request, Crud.UPDATE)

    country_info = get_object_or_404(CountryInfo, **{
        f'{CountryInfo.COUNTRY_FIELD}': country
    })

    return JsonResponse(replace_inner_html_payload(
        f"label[for='{form_auto_id(Address.STATE_FIELD)}']",
        country_info.subdivision
    ), status=HTTPStatus.OK)
