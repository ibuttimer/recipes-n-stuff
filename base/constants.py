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
from enum import Enum
from collections import namedtuple
from pathlib import Path

# name of this app
THIS_APP = Path(__file__).resolve().parent.name

# general context
APP_NAME_CTX = 'app_name'

# templates/base/snippet/info_title.html
TITLE_CTX = 'title'
TITLE_CLASS_CTX = 'title_class'
MODAL_LEVEL_CTX = 'modal_level'

InfoModalCfg = namedtuple(
    'InfoModalCfg',
    ['name', 'title_class', 'title_text'],
    defaults=['', '', '']
)
"""
Info modal configuration
name: info modal name
title_class: class to apply to title
title_text: title text
"""


class InfoModalLevel(Enum):
    """ Enum representing info modal levels """
    NONE = (0, InfoModalCfg(name='none'))
    DANGER = (1, InfoModalCfg(
        name='danger', title_class='text-danger', title_text='Danger'))
    WARN = (2, InfoModalCfg(
        name='warn', title_class='text-warning', title_text='Warning'))
    INFO = (3, InfoModalCfg(name='info', title_class='text-info'))
    QUESTION = (4, InfoModalCfg(name='question'))


exports = [
    'TITLE_CTX',
    'TITLE_CLASS_CTX',
    'MODAL_LEVEL_CTX',
    'InfoModalLevel',
]
