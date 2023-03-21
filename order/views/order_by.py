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

from .dto import OrderDto
from .order_queries import order_contains_subscription
from ..constants import (
    THIS_APP, ORDER_ID_ROUTE_NAME, ORDER_DTO_CTX, ORDER_REORDER_CTX
)
from utils import (
    Crud, app_template_path, reverse_q, namespaced_url
)
from .utils import order_permission_check


class OrderDetail(LoginRequiredMixin, View):
    """
    Class-based view for order get/update/delete
    """

    def get(self, request: HttpRequest, pk: int,
            *args, **kwargs) -> HttpResponse:
        """
        GET method for Order
        :param request: http request
        :param pk: id of address
        :param args: additional arbitrary arguments
        :param kwargs: additional keyword arguments
        :return: http response
        """
        order_permission_check(request, Crud.READ)

        order_dto = OrderDto.from_id(pk)

        return render(
            request, app_template_path(THIS_APP, 'order_view.html'),
            context={
                ORDER_DTO_CTX: order_dto,
                ORDER_REORDER_CTX: not order_contains_subscription(pk)
            }
        )

    def url(self, pk: int) -> str:
        """
        Get url for address update/delete
        :param pk: id of entity
        :return: url
        """
        return reverse_q(
            namespaced_url(THIS_APP, ORDER_ID_ROUTE_NAME),
            args=[pk]
        )
