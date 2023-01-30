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
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest

from utils import GET, PATCH, POST, DELETE, ModelMixin

ACTIONS = {
    GET: 'viewed',
    PATCH: 'updated',
    POST: 'updated',
    DELETE: 'deleted'
}


def raise_permission_denied(
        request: HttpRequest, model: ModelMixin, plural: str = 's'):
    """
    Raise a PermissionDenied exception
    :param request: http request
    :param model: model
    :param plural: model name pluralising addition; default 's'
    :raises: PermissionDenied
    """
    action = ACTIONS[request.method.upper()]
    raise PermissionDenied(
        f"{model.model_name_caps()}{plural} may only be {action} by "
        f"their owners")
