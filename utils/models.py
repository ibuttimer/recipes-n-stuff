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
from typing import Union, Type, Any, TypeVar, Optional, List, Tuple
from string import capwords

from django.db.models import Model, QuerySet
from django.shortcuts import get_object_or_404

# workaround for self type hints from https://peps.python.org/pep-0673/
TypeNameChoiceMixin = TypeVar("NameChoiceMixin", bound="NameChoiceMixin")
TypeModelMixin = TypeVar("ModelMixin", bound="ModelMixin")


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
    def id_field_query(cls, pk: int) -> dict:
        """
        Get an id field query
        :param pk: id of entity to search for
        :return: query dict
        """
        return {
            cls.id_field(): pk
        }

    @classmethod
    def get_by_field(cls, field: str, value: Any,
                     get_or_404: bool = True) -> Model:
        """
        Get an entity by the value of a field
        :param field: field to get by
        :param value: value to match
        :param get_or_404: get ot 404 flag; default True
        :return: model
        """
        query_param = {
            field: value
        }
        return get_object_or_404(cls, **query_param) if get_or_404 else \
            cls.objects.get(**query_param)

    @classmethod
    def filter_by_field(cls, field: str, value: Any) -> QuerySet:
        """
        Filter an entity by the value of a field
        :param field: field to filter by
        :param value: value to match
        :return: model
        """
        return cls.objects.filter(**{
            field: value
        })

    @classmethod
    def get_by_id_field(cls, pk: int, get_or_404: bool = True) -> Model:
        """
        Get an entity by its id field
        :param pk: id of entity to search for
        :param get_or_404: get ot 404 flag; default True
        :return: model
        """
        return cls.get_by_field(cls.id_field(), pk, get_or_404=get_or_404)

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
    def timedelta_fields(cls) -> list[str]:
        """ Get the list of timedelta fields """
        return []

    @classmethod
    def numeric_fields(cls) -> list[str]:
        """ Get the list of numeric fields """
        return []

    @classmethod
    def boolean_fields(cls) -> list[str]:
        """ Get the list of boolean fields """
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
    def is_timedelta_field(cls, field: str):
        """
        Check if the specified `field` is a timedelta
        :param field: field
        :return: True if `field` is a timedelta field
        """
        return field in cls.timedelta_fields()

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
    def is_timedelta_lookup(cls, lookup: str):
        """
        Check if the specified `lookup` represents a timedelta Lookup
        :param lookup: lookup string
        :return: True if lookup is a timedelta Lookup
        """
        return any(
            map(lambda fld: fld in lookup, cls.timedelta_fields())
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
    def is_boolean_lookup(cls, lookup: str):
        """
        Check if the specified `lookup` represents a boolean Lookup
        :param lookup: lookup string
        :return: True if lookup is a boolean Lookup
        """
        return any(
            map(lambda fld: fld in lookup, cls.boolean_fields())
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
        return cls.is_date_lookup(lookup) or cls.is_boolean_lookup(lookup) or \
            cls.is_timedelta_lookup(lookup) or \
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

    @classmethod
    def get_default_instance(
            cls, unique_fields: Optional[dict] = None,
            defaults: Optional[dict] = None) -> TypeModelMixin:
        """
        Get a default instance for objects requiring an instance of this model
        :param unique_fields: dict to use a keywords/values to look for
                            instance
        :param defaults: dict to use a keywords/values (in addition to
                            `unique_fields`) to create an instance
        :return: default instance
        """
        default_inst, _ = cls.objects.get_or_create(
            **unique_fields, defaults=defaults)
        return default_inst

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


class NameChoiceMixin:

    NAME = 'name'
    CHOICE = 'choice'

    def is_from_choice(self, choice: str) -> bool:
        """
        Check if the specified `choice` relates to this object
        :param choice: choice to check
        :return: True if choice matches
        """
        return self.value.choice.lower() == choice.lower()

    @property
    def display_name(self):
        """ Name value for this object """
        return self.value.name

    @property
    def choice(self):
        """ Choice value for this object """
        return self.value.choice

    @staticmethod
    def obj_from_choice(
            obj_type: TypeNameChoiceMixin, choice: str
    ) -> Optional[TypeNameChoiceMixin]:
        """
        Get the object corresponding to `choice`
        :param obj_type: NameChoice enum
        :param choice: choice to find
        :return: feature type or None of not found
        """
        choice = choice.lower()
        result = list(
            filter(lambda t: t.value.choice.lower() == choice, obj_type)
        )
        return result[0] if len(result) == 1 else None

    @staticmethod
    def get_model_choices(obj_type: TypeNameChoiceMixin) -> List[Tuple]:
        """
        Get the model choices for this object
        :param obj_type: NameChoice enum
        :return: list of choices
        """
        return [
            (entry.value.choice, entry.value.name) for entry in obj_type
        ]

    @staticmethod
    def assert_uniqueness(obj_type: TypeNameChoiceMixin):
        """
        Check that the objects names and choices are unique
        :param obj_type: NameChoice enum
        """
        for entry in obj_type:
            assert sum(
                map(lambda e: e.name == entry.name, obj_type)
            ) == 1
            assert sum(
                map(lambda e: e.choice == entry.choice, obj_type)
            ) == 1
