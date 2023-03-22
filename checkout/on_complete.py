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
from dataclasses import dataclass
from typing import Tuple, List, TypeVar, Optional

import json_fix
import jsonpickle
from django.apps import AppConfig

from django.http import HttpRequest

from checkout.constants import ON_COMPLETE_SES

TypeOnCompleteItem = TypeVar("TypeOnCompleteItem", bound="OnCompleteItem")
TypeOnComplete = TypeVar("TypeOnComplete", bound="OnComplete")


@dataclass
class OnCompleteItem:
    """ Class representing an on-complete item """
    model_name: str
    qs_filter: dict     # filter arguments
    qs_exclude: dict    # exclude arguments
    update: dict        # update arguments
    delete: bool        # perform delete flag

    @staticmethod
    def of_update(model_name: str, update: dict, qs_filter: dict = None,
                  qs_exclude: dict = None):
        """
        Create an update on-complete item
        :param model_name: name of model
        :param update: update to apply
        :param qs_filter: filter arguments; default None
        :param qs_exclude: exclude arguments; default None
        """
        return OnCompleteItem(model_name=model_name, qs_filter=qs_filter,
                              qs_exclude=qs_exclude, update=update,
                              delete=False)

    @staticmethod
    def of_delete(model_name: str, qs_filter: dict = None,
                  qs_exclude: dict = None):
        """
        Create a delete on-complete item
        :param model_name: name of model
        :param qs_filter: filter arguments; default None
        :param qs_exclude: exclude arguments; default None
        """
        return OnCompleteItem(model_name=model_name, qs_filter=qs_filter,
                              qs_exclude=qs_exclude, update=None,
                              delete=True)

    def execute(self):
        """
        Execute this item
        """
        model = AppConfig.get_model(self.model_name)
        queryset = model.objects
        if self.qs_filter:
            queryset = queryset.filter(**self.qs_filter)
        if self.qs_exclude:
            queryset = queryset.exclude(**self.qs_exclude)
        if self.update:
            queryset.update(**self.update)
        if self.delete:
            queryset.delete(**self.delete)

    def __json__(self):
        """ Return a built-in object that is naturally jsonable """
        return jsonpickle.encode(self)

    @staticmethod
    def from_jsonable(jsonable: dict) -> TypeOnCompleteItem:
        """
        Convert json representation to OnCompleteItem
        :param jsonable: json representation
        :return: OnCompleteItem if found otherwise original argument
        """
        return jsonpickle.decode(jsonable)


class OnComplete:
    """ Class representing an on-complete list """
    items: List[OnCompleteItem] = []
    closed: bool = True

    def __init__(self, request: HttpRequest = None):
        self._initialise()
        self._new_list(request)

    def _initialise(self):
        """
        Initialise the on-complete
        """
        self.items = []

    def _new_list(self, request: HttpRequest):
        """
        Start a new on-complete
        :param request: http request
        """
        if self.closed:
            if request and request.user.is_authenticated:
                self._initialise()
                self.closed = False
            else:
                self.closed = True

    def add_update(self, request: HttpRequest, model_name: str, update: dict,
                   qs_filter: dict = None, qs_exclude: dict = None):
        """
        Add an update-item to the on-complete
        :param request: http request
        :param model_name: name of model
        :param update: update to apply
        :param qs_filter: filter arguments; default None
        :param qs_exclude: exclude arguments; default None
        """
        self._new_list(request)

        self.items.append(OnCompleteItem.of_update(
            model_name, update, qs_filter=qs_filter, qs_exclude=qs_exclude
        ))

    def add_delete(self, request: HttpRequest, model_name: str,
                   qs_filter: dict = None, qs_exclude: dict = None):
        """
        Add a delete-item to the on-complete
        :param request: http request
        :param model_name: name of model
        :param qs_filter: filter arguments; default None
        :param qs_exclude: exclude arguments; default None
        """
        self._new_list(request)

        self.items.append(OnCompleteItem.of_delete(
            model_name, qs_filter=qs_filter, qs_exclude=qs_exclude
        ))

    def execute(self):
        """
        Execute this on-complete list
        """
        for item in self.items:
            item.execute()

    def get_item(self, index: int) -> Optional[OnCompleteItem]:
        """
        Get an item from the on-complete
        :param index: index of item
        """
        item = None
        if 0 <= index < self.num_items:
            item = self.items[index]
        return item

    def remove(self, index: int) -> bool:
        """
        Remove an item from the on-complete
        :param index: index of item
        :return: True if basket updated
        """
        success = False
        if 0 <= index < self.num_items:
            del self.items[index]
            success = True
        return success

    def clear(self, request: HttpRequest = None):
        """
        Clear the on-complete
        """
        self._initialise()
        self.add_to_request(request)

    def close(self, request: HttpRequest = None):
        """
        Close the on-complete
        """
        self.closed = True
        self.add_to_request(request)

    def add_to_request(self, request: HttpRequest):
        """
        Add this on-complete to the request session.
        :param request: http request
        """
        if request:
            request.session[ON_COMPLETE_SES] = self

    def close(self, request: HttpRequest = None):
        """
        Close this on-complete
        """
        self.closed = True
        self.add_to_request(request)

    @property
    def num_items(self) -> int:
        """
        Get number of items in the basket
        :return: number of items
        """
        return len(self.items)

    def __json__(self):
        """ Return a built-in object that is naturally jsonable """
        return jsonpickle.encode(self)

    @staticmethod
    def from_jsonable(jsonable: dict) -> TypeOnComplete:
        """
        Convert json representation to OnComplete
        :param jsonable: json representation
        :return: OnComplete if found otherwise original argument
        """
        return jsonpickle.decode(jsonable)


def get_on_complete(request: HttpRequest) -> Tuple[OnComplete, bool]:
    """
    Get the session on-complete list
    :param request: http request
    :return tuple of on-complete list and new list flag
    """
    new_list = ON_COMPLETE_SES not in request.session
    if new_list:
        on_complete = OnComplete(request=request)
    else:
        session_attrib = request.session[ON_COMPLETE_SES]
        on_complete = \
            session_attrib if isinstance(session_attrib, OnComplete) else \
            OnComplete.from_jsonable(session_attrib)
    on_complete.add_to_request(request)
    return on_complete, new_list
