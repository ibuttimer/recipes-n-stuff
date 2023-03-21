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

from typing import List

from base.dto import ImagePool
from recipes.templatetags.stock_image import stock_image


def recipe_main_image(images: List) -> ImagePool:
    """
    The url for the main image
    :return: url str or None
    """
    # first image in list and a backup stock image
    online_img = len(images) > 0
    return ImagePool(
        url=images[0].url if online_img else None, is_static=not online_img
    ).add_image(url=stock_image(), is_static=True)


def recipe_image_pool(images: List) -> List[ImagePool]:
    """
    The recipe image pool list
    :return: list of images or None
    """
    if len(images) == 0:
        pool = ImagePool.of_static(stock_image())
    else:
        pool = ImagePool.of_url(images[0].url)
        for idx in range(1, len(images)):
            pool.add_image(images[idx].url, is_static=False)
    return pool
