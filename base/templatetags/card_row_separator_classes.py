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
#
import math
from typing import Union

from django import template

from .attr_append import attr_append

register = template.Library()

# https://docs.djangoproject.com/en/4.1/howto/custom-template-tags/#simple-tags

# Bootstrap breakpoints
XS = 0x01       # xs <576px
SM = 0x02       # sm ≥576px
MD = 0x04       # md ≥768px
LG = 0x08       # lg ≥992px
XL = 0x10       # xl ≥1200px
XXL = 0x20      # xxl ≥1400px
NUM_BREAKS = 6

BREAKPOINT_TAG = {
    XS: 'xs',
    SM: 'sm',
    MD: 'md',
    LG: 'lg',
    XL: 'xl',
    XXL: 'xxl',
}
BREAKPOINT_ID = {
    # xs is ''
    key: '' if val == 'xs' else val for key, val in BREAKPOINT_TAG.items()
}


@register.simple_tag
def card_row_separator_classes(per_row: int, breakpoints: int,
                               hide_above: bool = False,
                               append: str = '', check: bool = True):
    """
    Generate the card row separator classes for card-row-separator.html for
    the specified number of cards per row, with optional append string
    depending on truthy-ness of `check`
    :param per_row: number of cards per row
    :param breakpoints: mask of values representing bootstrap breakpoints
    :param hide_above: hide above breakpoints flag; default False
    :param append: string to append; default ''
    :param check: condition to check; default True
    :return: string
    """
    assert per_row > 0
    # if per_row == 1:
    #     # full width column every 2nd loop when counter divisible by 1 but
    #     # only visible below sm breakpoint, i.e. 1 card per row
    #     class_attrib = 'col-12 d-sm-none'
    # else:

    # https://getbootstrap.com/docs/5.3/utilities/display/#hiding-elements
    # takes the form
    # 'col-12 d-none <visible-breakpoint-block> <hidden-above-breakpoint>"
    # e.g. 'col-12 d-none d-sm-block d-md-block d-lg-none'
    # full width column every nth loop when counter divisible by n but
    # only visible for breakpoints sm & md i.e. n cards per row
    breakpoints = breakpoint_arg(breakpoints)
    first_bit = get_first_set_bit_pos(breakpoints) - 1  # 0-based index
    assert first_bit >= 0
    attribs = []
    for shft in range(first_bit, NUM_BREAKS):
        break_pt = 0x01 << shft
        if break_pt & breakpoints:
            # add visible breakpoint blocks
            attribs.append(class_block(break_pt))
        else:
            if hide_above:
                # add hidden above breakpoint none
                attribs.append(class_none(break_pt))
            break
    class_attrib = f'col-12 d-none {" ".join(attribs)}'
    class_attrib = class_attrib.replace('d-none d-block', 'd-block')

    return attr_append(
        f'class="{class_attrib}"', append, check=check
    )


def class_display(break_pt: int, value: str):
    """
    Generate a Bootstrap display class; e.g. 'd-sm-none'
    https://getbootstrap.com/docs/5.3/utilities/display/
    :param break_pt: one of XS, SM etc.
    :param value: one of notation values; 'none', 'inline' etc.
        https://getbootstrap.com/docs/5.3/utilities/display/#notation
    :return: class
    """
    tag = f"-{BREAKPOINT_ID[break_pt]}" if BREAKPOINT_ID[break_pt] else ''
    return f'd{tag}-{value}'


def class_block(break_pt: int):
    """
    Generate a Bootstrap display block class; e.g. 'd-sm-block'
    :param break_pt: one of XS, SM etc.
    :return: class
    """
    return class_display(break_pt, 'block')


def class_none(break_pt: int):
    """
    Generate a Bootstrap display none class; e.g. 'd-sm-none'
    :param break_pt: one of XS, SM etc.
    :return: class
    """
    return class_display(break_pt, 'none')


def get_first_set_bit_pos(num: int) -> int:
    """
    Get the index of the first set bit position
    Courtesy of https://www.geeksforgeeks.org/position-of-rightmost-set-bit/
    :param num: number to get first set bit position of
    :return: 1-based index
    """
    return int(math.log2(num & -num) + 1)


def breakpoint_arg(breakpoints: Union[int, str]) -> int:
    if isinstance(breakpoints, str):
        breakpoints = breakpoints.lower()
        if breakpoints.isnumeric() or breakpoints.startswith('0x'):
            # breakpoint bit mask
            base = 16 if breakpoints.lower().startswith('0x') else 10
            breakpoints = int(breakpoints, base=base)
        else:
            # breakpoint names; e.g. 'sm-md'
            splits = breakpoints.split('-')
            start = tag_id(splits[0])
            end = tag_id(splits[1]) if len(splits) > 1 else start
            assert start <= end
            breakpoints = sum(
                [0x01 << shft for shft in range(
                    int(math.log2(start)), int(math.log2(end)) + 1)]
            )
    return breakpoints


def tag_id(tag: str) -> int:
    tag = tag.lower()
    for tid, bk_tag in BREAKPOINT_TAG.items():
        if bk_tag == tag:
            bk_id = tid
            break
    else:
        bk_id = 0
    return bk_id
