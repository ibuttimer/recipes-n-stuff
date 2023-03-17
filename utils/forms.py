#  MIT License
#
#  Copyright (c) 2022 Ian Buttimer
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

from collections import namedtuple
from string import Template, capwords

from typing import Type, Union, NoReturn, List, Tuple, Optional

from django.core.validators import (
    MaxValueValidator, MinValueValidator, MinLengthValidator,
    MaxLengthValidator
)
from django.forms import BaseForm
from django.utils.translation import gettext_lazy as _


ALL_FIELDS = "__all__"


_ATTRIB = 'attrib'
_ATTRIB_VAL = 'attrib_val'
_MAX_LEN = MaxLengthValidator.code
_MIN_LEN = MinLengthValidator.code
_MAX_VAL = MaxValueValidator.code
_MIN_VAL = MinValueValidator.code
# from django.forms.fields.Field.default_error_messages dict
_REQUIRED = 'required'
_FROM_LIST = 'from_list'
# combined error message combining all the other messages
_COMBINED = 'combined'

_STATEMENT_ATTRIBS = [_REQUIRED, _FROM_LIST]
_NO_VAL_ATTRIBS = _STATEMENT_ATTRIBS.copy()
_NO_VAL_ATTRIBS.append(_ATTRIB)

ErrorMsgs: Type[tuple] = namedtuple(
    'ErrorMsgs',
    [_ATTRIB, _MAX_LEN, _MIN_LEN, _MAX_VAL, _MIN_VAL, _REQUIRED, _FROM_LIST],
    defaults=['', None, None, None, None, None, None]
)

# keys are error codes of ValidationError raised by validator
# (except 'combined' which is made up)
_msg_templates = {
    _MIN_LEN: Template(f'Minimum length for ${_ATTRIB} is ${_ATTRIB_VAL}.'),
    _MAX_LEN: Template(f'Maximum length for ${_ATTRIB} is ${_ATTRIB_VAL}.'),
    _MIN_VAL: Template(f'Minimum value for ${_ATTRIB} is ${_ATTRIB_VAL}.'),
    _MAX_VAL: Template(f'Maximum value for ${_ATTRIB} is ${_ATTRIB_VAL}.'),
    _REQUIRED: Template(f'Please enter ${_ATTRIB}, it is required.'),
    _FROM_LIST: Template(f'Please select ${_ATTRIB} from list.')
}
_description = {
    _MIN_LEN: 'minimum length',
    _MAX_LEN: 'maximum length',
    _MIN_VAL: 'minimum value',
    _MAX_VAL: 'maximum value',
    _REQUIRED: 'is required',
    _FROM_LIST: 'select from list',
}


def error_messages(model: str, *args: ErrorMsgs) -> dict:
    """
    Generate error texts for the specified attributes of 'model'.
    Note: currently only supports min/max length.
    :param model:   name of model
    :param args:    list of attributes
    :return: dict of help texts of the form 'Model attrib.'
    """
    def inc_msg(fld: str, err_msg: ErrorMsgs, exclude: List[str] = None):
        # Check if field is not attrib & value is not None
        if exclude is None:
            exclude = [_ATTRIB]
        return fld not in exclude and getattr(err_msg, fld) is not None

    def combined_msg(err_msg: ErrorMsgs):
        msg = capwords(getattr(err_msg, _ATTRIB))
        terms = [
            f'{_description[k]}' for k in _STATEMENT_ATTRIBS
            if inc_msg(k, entry)
        ]
        terms.extend([
            f'{_description[k]} {getattr(entry, k)}'
            for k in ErrorMsgs._fields
            if inc_msg(k, entry, exclude=_NO_VAL_ATTRIBS)
        ])
        if len(terms) > 1:
            msg = f'{msg}: {",".join(terms[:-1])} and {terms[-1]}'
        elif len(terms) > 0:
            msg = f'{msg} {terms[-1]}'
        return f'{msg}.'

    messages = {}
    for entry in args:
        messages[entry.attrib] = {
            _COMBINED: combined_msg(entry)
        }
        messages[entry.attrib].update(dict(
            zip(
                [k for k in ErrorMsgs._fields if inc_msg(k, entry)],
                [_msg_templates[k].substitute({
                    _ATTRIB: capwords(entry.attrib),
                    _ATTRIB_VAL: getattr(entry, k)
                }) for k in ErrorMsgs._fields if inc_msg(k, entry)]
            )
        ))
    return messages


def update_field_widgets(form: BaseForm,
                         fields: Union[list[str], tuple[str], str],
                         attrs_update: dict) -> NoReturn:
    """
    Update the widget attributes for the specified fields in 'form'.
    :param form:        django form
    :param fields:      list of names of fields to update, or use '__all__' to
                        update all fields
    :param attrs_update:    updates to apply to widgets
    """
    fld_names: list
    if fields == ALL_FIELDS:
        fld_names = form.fields.keys()
    else:
        fld_names = fields
    for name in fld_names:
        form.fields[name].widget.attrs.update(attrs_update)


def form_auto_id(field_name: str):
    """
    Get a form field id as generated by django
    :param field_name: field name
    :return: field auto id
    """
    return f'id_{field_name}'


class FormMixin:
    """ Mixin to provide custom form utility functions """

    def add_bootstrap(
            self, fields: Union[List[str], Tuple[str], str],
            attrs: dict, exclude: Optional[List[str]] = None):
        """
        Add bootstrap classes
        :param fields:  list of names of fields to update, or use
                '__all__' to update all fields
        :param attrs: widget attributes
        :param exclude: list of names of fields to exclude
        """
        if exclude is None:
            exclude = []
        update_field_widgets(
            self,
            # exclude non-bootstrap fields
            [field for field in fields if field not in exclude], attrs)

    def add_form_control(
            self, fields: Union[List[str], Tuple[str], str],
            exclude: Optional[List[str]] = None):
        """
        Add bootstrap classes
        :param fields:  list of names of fields to update, or use
                '__all__' to update all fields
        :param exclude: list of names of fields to exclude
        """
        self.add_bootstrap(fields, {
            'class': 'form-control'
        }, exclude=exclude)

    def add_form_check_input(
            self, fields: Union[List[str], Tuple[str], str],
            exclude: Optional[List[str]] = None):
        """
        Add bootstrap classes
        :param fields:  list of names of fields to update, or use
                '__all__' to update all fields
        :param exclude: list of names of fields to exclude
        """
        self.add_bootstrap(fields, {
            'class': 'form-check-input'
        }, exclude=exclude)
