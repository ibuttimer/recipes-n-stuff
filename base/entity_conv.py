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
import json
import os
import re
from pathlib import Path

# dict with entity name as key and char as value
_ENTITY_CHAR_MAP = None
# dict with code point as key and entity name as value
_CODE_PT_ENTITY_MAP = None
# https://html.spec.whatwg.org/multipage/named-characters.html json field names
CODE_PTS = "codepoints"
CHARS = "characters"

ENTITY_REGEX = re.compile(r'(&[a-zA-Z]+;)')


def init_entity_conv():
    """ Initialise html entity conversion """
    global _ENTITY_CHAR_MAP, _CODE_PT_ENTITY_MAP
    if _ENTITY_CHAR_MAP is None:
        folder = Path(__file__).resolve().parent
        filepath = os.path.join(folder, 'entities.json')

        with open(filepath, encoding='utf-8') as fp:
            raw_refs = json.load(fp)
            _ENTITY_CHAR_MAP = {}
            _CODE_PT_ENTITY_MAP = {}
            for entity, data in raw_refs.items():
                if not entity[-1] == ';':
                    continue    # skip legacy without the trailing semicolon
                # only need single codepoint entities
                if len(data[CODE_PTS]) == 1:
                    _ENTITY_CHAR_MAP[entity] = data[CHARS]
                    _CODE_PT_ENTITY_MAP[data[CODE_PTS][0]] = entity


def _cp_to_entity(val, do_ascii: bool = False):
    """
    Convert a unicode codepoint to a string
    :param val: unicode codepoint
    :param do_ascii: encode ascii char flag; default False
    :return: string
    """
    do_conv = val in _CODE_PT_ENTITY_MAP and \
        ((val <= 0x7f and do_ascii) or (val > 0x7f))
    return _CODE_PT_ENTITY_MAP[val] if do_conv else chr(val)


def _entity_to_chr(val):
    """
    Convert a html entity to unicode string
    :param val: html entity
    :return: string
    """
    return _ENTITY_CHAR_MAP[val] if val in _ENTITY_CHAR_MAP else val


def escape_entities(text: str, do_ascii: bool = False):
    """
    Escape the specified string; i.e. convert chars to HTML entities where
    required
    :param text: text to convert
    :param do_ascii: encode ascii char flag; default False
    :return: escaped string
    """
    global _ENTITY_CHAR_MAP
    if _ENTITY_CHAR_MAP is None:
        init_entity_conv()

    return ''.join(
        _cp_to_entity(ord(char), do_ascii=do_ascii) for char in text)


def unescape_entities(text: str):
    """
    Unescape the specified string; i.e. convert HTML entities to chars where
    required
    :param text: text to convert
    :return: unescaped string
    """
    global _ENTITY_CHAR_MAP
    if _ENTITY_CHAR_MAP is None:
        init_entity_conv()

    return re.sub(
        ENTITY_REGEX, lambda match: _entity_to_chr(match.group(0)), text)
