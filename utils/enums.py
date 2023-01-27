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
from enum import Enum, auto
from typing import TypeVar, Any, Callable, Optional, Type, Union

# workaround for self type hints from https://peps.python.org/pep-0673/
TypeChoiceArg = TypeVar("TypeChoiceArg", bound="ChoiceArg")
TypeQueryStatus = TypeVar("TypeQueryStatus", bound="QueryStatus")
TypeQueryArg = TypeVar("QueryArg", bound="QueryArg")
TypeQueryOption = TypeVar("TypeQueryOption", bound="QueryOption")


class ChoiceArg(Enum):
    """ Enum representing options with limited choices """
    display: str
    """ Display string """
    arg: Any
    """ Argument value """

    def __init__(self, display: str, arg: Any):
        self.display = display
        self.arg = arg

    @staticmethod
    def _lower_str(val):
        """ Lower string value function for filtering """
        return val.lower() if isinstance(val, str) else val

    @staticmethod
    def _pass_thru(val):
        """ Pass-through filter function """
        return val

    @classmethod
    def _find_value(
            cls, arg: Any, func: Callable = None) -> Optional[TypeChoiceArg]:
        """
        Get value matching specified `arg`
        :param arg: arg to find
        :param func: value transform function to be applied before comparison;
                     default pass-through
        :return: ChoiceArg value or None if not found or multiple matches
        """
        if func is None:
            func = cls._pass_thru

        matches = list(
            filter(
                lambda val: func(val) == arg,
                cls
            )
        )
        return matches[0] if len(matches) == 1 else None

    @classmethod
    def from_arg(
            cls, arg: Any, func: Callable = None) -> Optional[TypeChoiceArg]:
        """
        Get value matching specified `arg`
        :param arg: arg to find
        :param func: value transform function to be applied before comparison;
                     default convert to lower-case string
        :return: ChoiceArg value or None if not found or multiple matches
        """
        if func is None:
            def trans_func(val):
                return cls._lower_str(val.arg)
            func = trans_func

        return cls._find_value(arg, func=func)

    @classmethod
    def from_display(
            cls, display: str, func: Callable = None
    ) -> Optional[TypeChoiceArg]:
        """
        Get value matching specified display string
        :param display: display string to find
        :param func: value transform function to be applied before comparison;
                     default convert to lower-case string
        :return: ChoiceArg value or None if not found
        """
        if func is None:
            def trans_func(val):
                return cls._lower_str(val.display)
            func = trans_func
            display_func = cls._lower_str
        else:
            display_func = cls._pass_thru

        return cls._find_value(display_func(display), func=func)

    @staticmethod
    def arg_if_choice_arg(obj):
        """
        Get the value if `obj` is a ChoiceArg, otherwise `obj`
        :param obj: object to get value of
        :return: value
        """
        return obj.arg \
            if isinstance(obj, ChoiceArg) else obj


class QueryArg:
    """ Class representing request query args """
    value: Any
    """ Value """
    was_set: bool
    """ Argument was set in request flag """

    def __init__(self, value: Any, was_set: bool):
        self.set(value, was_set)

    def set(self, value: Any, was_set: bool):
        """
        Set the value and was set flag
        :param value:
        :param was_set:
        :return:
        """
        self.value = value
        self.was_set = was_set

    def was_set_to(self, value: Any, attrib: str = None):
        """
        Check if value was to set the specified `value`
        :param value: value to check
        :param attrib: attribute of set value to check; default None
        :return: True if value was to set the specified `value`
        """
        chk_value = self.value if not attrib else getattr(self.value, attrib)
        return self.was_set and chk_value == value

    @property
    def value_arg_or_value(self) -> Any:
        """
        Get the arg value if this object's value is a ChoiceArg, otherwise
        this object's value
        :return: value
        """
        return self.value.arg \
            if isinstance(self.value, ChoiceArg) else self.value

    @staticmethod
    def value_arg_or_object(obj) -> Any:
        """
        Get the arg value if `obj` is a ChoiceArg, otherwise `obj`
        :param obj: object to get value of
        :return: value
        """
        return ChoiceArg.arg_if_choice_arg(obj.value) \
            if isinstance(obj, QueryArg) else obj

    @staticmethod
    def of(obj) -> TypeQueryArg:
        """
        Get an unset QueryArg with the value 0f `obj`
        :param obj: value
        :return: new QueryArg
        """
        return QueryArg(obj, False)

    def __str__(self):
        return f'{self.value}, was_set {self.was_set}'


QueryArg.NONE = QueryArg.of(None)


@dataclass
class QueryOption:
    """
    Request query option class
    """
    query: str
    """ Query key """
    clazz: Optional[Type[ChoiceArg]]
    """ Class of choice result """
    default: Union[ChoiceArg, Any]
    """ Default choice """

    @classmethod
    def of_no_cls_dflt(
            cls: Type[TypeQueryOption], query: str) -> TypeQueryOption:
        """ Get QueryOption with no class or default """
        return cls(query=query, clazz=None, default=None)

    @classmethod
    def of_no_cls(
        cls: Type[TypeQueryOption], query: str, default: Union[ChoiceArg, Any]
    ) -> TypeQueryOption:
        """ Get QueryOption with no class or default """
        return cls(query=query, clazz=None, default=default)


class SortOrder(ChoiceArg):
    """ Base enum representing sort orders """

    def __init__(self, display: str, arg: str, order: str):
        super().__init__(display, arg)
        self.order = order


class PerPage(ChoiceArg):
    """ Enum representing opinions per page """
    SIX = 6
    NINE = 9
    TWELVE = 12
    FIFTEEN = 15

    def __init__(self, count: int):
        super().__init__(f'{count} per page', count)


PerPage.DEFAULT = PerPage.SIX


class YesNo(ChoiceArg):
    """ Enum representing a truthy choice """
    NO = ('No', 'no')
    YES = ('Yes', 'yes')
    IGNORE = ('Ignore', 'na')

    @property
    def boolean(self) -> Optional[bool]:
        """ Boolean representation of choice """
        return True if self == YesNo.YES else \
            False if self == YesNo.NO else None


YesNo.DEFAULT = YesNo.IGNORE
