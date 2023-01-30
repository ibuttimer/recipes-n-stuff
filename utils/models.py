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
from typing import Union, Type, Any
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
        Get the model name of this object
        :return: model name
        """
        return ModelMixin.model_name_obj(cls)

    @classmethod
    def model_name_caps(cls):
        """
        Get the caps model name of this object
        :return: model name
        """
        return capwords(cls.model_name())

    @classmethod
    def model_name_lower(cls):
        """
        Get the lowercase model name of this object
        :return: model name
        """
        return cls.model_name().lower()

    @classmethod
    def date_fields(cls) -> list[str]:
        """ Get the list of date fields """
        return []

    @classmethod
    def numeric_fields(cls) -> list[str]:
        """ Get the list of numeric fields """
        return []

    @classmethod
    def is_date_field(cls, field: str):
        """
        Check if the specified `field` is a date
        :param field: field
        :return: True if `field` is a date field
        """
        return field in cls.date_fields()

    @classmethod
    def is_numeric_field(cls, field: str):
        """
        Check if the specified `field` is numeric
        :param field: field
        :return: True if `field` is a numeric field
        """
        return field in cls.numeric_fields()

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
    def is_numeric_lookup(cls, lookup: str):
        """
        Check if the specified `lookup` represents a numeric Lookup
        :param lookup: lookup string
        :return: True if lookup is a numeric Lookup
        """
        return any(
            map(lambda fld: fld in lookup, cls.numeric_fields())
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

    @classmethod
    def is_non_text_lookup(cls, lookup: str):
        """
        Check if the specified `lookup` represents a non-text Lookup
        :param lookup: lookup string
        :return: True if lookup is not a text lookup
        """
        return cls.is_date_lookup(lookup) or \
            cls.is_numeric_lookup(lookup) or cls.is_id_lookup(lookup)

    @classmethod
    def date_lookup(cls, field: str, oldest_first: bool = True) -> str:
        """
        Make a date lookup
        :param field: name of date field
        :param oldest_first: oldest first flag; default True
        :return: lookup string
        """
        return \
            f'{DATE_OLDEST_LOOKUP if oldest_first else DATE_NEWEST_LOOKUP}' \
            f'{field}'

    def get_field(self, field: str, raise_ex: bool = True) -> Any:
        """
        Get the value of a specified field
        :param field: name of field
        :param raise_ex: raise exception if field not found; default True
        :return: field value or None if not found
        :raises: ValueError if field not found and `raise_ex` is True
        """
        if field not in self.__dict__ and raise_ex:
            raise ValueError(f'{field} not found')
        return self.__dict__.get(field, None)

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
