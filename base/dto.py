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
from copy import deepcopy
from dataclasses import dataclass

from django.db.models import Model


@dataclass
class BaseDto:
    """ Base data transfer object """

    add_new: bool = False
    """ Add new placeholder flag"""

    @staticmethod
    def from_model_to_obj(model: Model, instance):
        """
        Generate a DTO from the specified `model`
        :param model: model class
        :param instance: DTO instance to populate
        :return: updated instance
        """
        for key in list(model.__dict__.keys()):
            if key.startswith('_'):
                continue
            setattr(instance, key, deepcopy(getattr(model, key)))
        return instance

    @staticmethod
    def to_add_new_obj(instance):
        """
        Generate add new placeholder a DTO from the specified `instance`
        :param instance: DTO instance to update
        :return: updated instance
        """
        instance.add_new = True
        return instance
