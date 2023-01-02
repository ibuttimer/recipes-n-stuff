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

from inspect import isclass
from typing import Union, Type
from string import capwords

from django.db.models import Model


# sorting related
DESC_LOOKUP = '-'
""" Lookup order for descending sort """
DATE_OLDEST_LOOKUP = ''
""" Lookup order for ascending date, i.e. oldest first """
DATE_NEWEST_LOOKUP = DESC_LOOKUP
""" Lookup order for descending date, i.e. newest first """


class ModelMixin:
    """ Mixin with additional functionality for django.db.models.Model """

    @staticmethod
    def model_name_obj(obj: Union[object, Model]):
        """
        Get the model name of the specified model class/instance
        :param obj: object to check
        :return: model name
        """
        return obj._meta.model_name \
            if isclass(obj) else obj.__class__._meta.model_name

    @classmethod
    def id_field(cls):
        """ The id (primary key) field name """
        return cls._meta.pk.name

    @classmethod
    def model_name(cls):
        """
        Get the model name of this model
        :return: model name
        """
        return ModelMixin.model_name_obj(cls)

    @classmethod
    def model_name_caps(cls):
        """
        Get the model name of this model
        :return: model name
        """
        return capwords(cls.model_name())

    @classmethod
    def model_name_lower(cls):
        """
        Get the model name of this model
        :return: model name
        """
        return cls.model_name().lower()

    @classmethod
    def date_fields(cls) -> list[str]:
        """ Get the list of date fields """
        return []

    @classmethod
    def is_date_field(cls, field: str):
        """
        Check if the specified `field` is a date field
        :param field: field
        :return: True if `field` contains a date field
        """
        return field in cls.date_fields()

    @classmethod
    def is_date_lookup(cls, lookup: str):
        """
        Check if the specified `lookup` represents a date Lookup
        :param lookup: lookup string
        :return: True if lookup is a date Lookup
        """
        return any(
            map(lambda fld: fld in lookup, cls.date_fields())
        )

    @classmethod
    def is_id_lookup(cls, lookup: str):
        """
        Check if the specified `lookup` represents an id Lookup
        :param lookup: lookup string
        :return: True if lookup is an id lookup
        """
        lookup = lookup.lower()
        return lookup == cls.id_field() or \
            lookup == f'{DESC_LOOKUP}{cls.id_field()}'

    def __repr__(self):
        return f'{self.model_name()}[{self.id}]: {str(self)}'


class ModelFacadeMixin:
    """
    A facade allowing non-django.db.models.Models objects to appear as Models
    """

    @classmethod
    def lookup_clazz(cls) -> Type[Model]:
        """ Get the Model class """
        if not issubclass(cls, Model):
            raise NotImplementedError(
                "Non-Model objects must override the 'lookup_clazz' method")
        return cls
