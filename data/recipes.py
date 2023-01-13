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

# Script to load a set of standard data to the database

import os
import sys
from enum import IntEnum, auto
from pathlib import Path
import re
import csv
import argparse
from string import capwords

import environ
import psycopg2
import pyarrow
from django.conf import settings
from django_countries import countries
import pyarrow.parquet as pq
import pyarrow.compute as pc
from psycopg2.extras import execute_batch

from data.data_utils import insert_content, get_content_id, insert_batch

# recipe parquet
RECIPES_PARQUET = 'recipes.parquet'
# table.schema.names
COL_NAMES = [
    'RecipeId', 'Name', 'AuthorId', 'AuthorName', 'CookTime', 'PrepTime',
    'TotalTime', 'DatePublished', 'Description', 'Images', 'RecipeCategory',
    'Keywords', 'RecipeIngredientQuantities', 'RecipeIngredientParts',
    'AggregatedRating', 'ReviewCount', 'Calories', 'FatContent',
    'SaturatedFatContent', 'CholesterolContent', 'SodiumContent',
    'CarbohydrateContent', 'FiberContent', 'SugarContent', 'ProteinContent',
    'RecipeServings', 'RecipeYield', 'RecipeInstructions'
]


class Cols(IntEnum):
    """
    Enum representing column names
    Based on https://stackoverflow.com/a/61438054/4054609
    """

    def _generate_next_value_(name, start, count, last_values):
        """ generate consecutive automatic numbers starting from zero """
        return count

    RecipeId = auto()
    Name = auto()
    AuthorId = auto()
    AuthorName = auto()
    CookTime = auto()
    PrepTime = auto()
    TotalTime = auto()
    DatePublished = auto()
    Description = auto()
    Images = auto()
    RecipeCategory = auto()
    Keywords = auto()
    RecipeIngredientQuantities = auto()
    RecipeIngredientParts = auto()
    AggregatedRating = auto()
    ReviewCount = auto()
    Calories = auto()
    FatContent = auto()
    SaturatedFatContent = auto()
    CholesterolContent = auto()
    SodiumContent = auto()
    CarbohydrateContent = auto()
    FiberContent = auto()
    SugarContent = auto()
    ProteinContent = auto()
    RecipeServings = auto()
    RecipeYield = auto()
    RecipeInstructions = auto()


CATEGORY_TABLE = 'recipes_category'
CATEGORY_NAME = 'name'
CATEGORY_FIELDS = [CATEGORY_NAME]
KEYWORD_TABLE = 'recipes_keyword'
KEYWORD_NAME = 'name'
KEYWORD_FIELDS = [KEYWORD_NAME]

categories = {}     # key: category, val: id
keywords = {}       # key: keyword, val: id


def load_recipe(args: argparse.Namespace, curs):
    # load recipe info
    folder = Path(args.data_folder).resolve()
    filepath = os.path.join(folder, RECIPES_PARQUET)

    table = pq.read_table(filepath)

    # process category
    progress = Progress('Category', args.progress, CATEGORY_TABLE)
    progress.start()
    for category in pc.unique(table[COL_NAMES[Cols.RecipeCategory]]):
        if not category:
            continue

        new_id = insert_content(
            curs, CATEGORY_FIELDS, (category, ), CATEGORY_TABLE, unique=True)
        categories[str(category)] = \
            new_id or \
            get_content_id(curs, CATEGORY_TABLE, CATEGORY_NAME, category)

        progress.inc()

    progress.end()

    # process keywords
    progress.reset('Keyword', args.progress, KEYWORD_TABLE)
    progress.start()
    for words in table[COL_NAMES[Cols.Keywords]]:
        if not words:
            continue

        for word in words.as_py():
            if not word:
                continue

            new_id = insert_content(
                curs, KEYWORD_FIELDS, (word, ), KEYWORD_TABLE, unique=True)
            keywords[str(word)] = \
                new_id or \
                get_content_id(curs, KEYWORD_TABLE, KEYWORD_NAME, word)
        progress.inc()

    progress.end()


class Progress:

    title: str
    tick: int
    table: str
    processed: int
    size: int

    def __init__(self, title: str, tick: int, table: str):
        self.reset(title, tick, table)

    def reset(self, title: str, tick: int, table: str):
        self.title = title
        self.tick = tick
        self.table = table
        self.processed = 0
        self.size = 0

    def start(self):
        self.processed = 0
        self.size = 0
        print(f'{self.title}: Processing ', end='')

    def inc(self):
        self.processed += 1
        if self.processed % self.tick == 0:
            progress = f'{self.processed}'
            backspace = '\b' * self.size if self.size else ''
            self.size = len(progress)
            print(f'{backspace}{progress}', end='')

    def end(self):
        print(f'\n{self.title}: Processed {self.processed} entries for '
              f'{self.table}')
