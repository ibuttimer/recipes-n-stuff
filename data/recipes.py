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

import argparse
import os
import pickle
from enum import IntEnum, auto
from pathlib import Path
from typing import Optional, Callable

import pyarrow.compute as pc
import pyarrow.parquet as pq

from data.data_utils import insert_content, get_content_id

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
MEASURE_TABLE = 'recipes_measure'
MEASURE_NAME = 'name'
INGREDIENT_TABLE = 'recipes_ingredient'
INGREDIENT_NAME = 'name'
INGREDIENT_MEASURE = 'measure_id'
INGREDIENT_FIELDS = [INGREDIENT_NAME, INGREDIENT_MEASURE]
IMAGE_TABLE = 'recipes_image'
IMAGE_NAME = 'name'
IMAGE_FIELDS = [IMAGE_NAME]

categories = {}     # key: category, val: id
keywords = {}       # key: keyword, val: id
ingredients = {}    # key: keyword, val: id


def load_recipe(args: argparse.Namespace, curs):
    """
    Load recipe data
    :param args: program arguments
    :param curs: cursor
    """
    # load recipe info
    folder = Path(args.data_folder).resolve()
    filepath = os.path.join(folder, RECIPES_PARQUET)

    table = pq.read_table(filepath)

    # process category
    progress = Progress('Category', args.progress, CATEGORY_TABLE)
    skip = args.skip_category
    if skip:
        data, pickle_file = unpickle_data(CATEGORY_TABLE, folder)
        if data:
            categories.update(data)

            progress.skip(f'- read ids from {pickle_file}')
        else:
            # need to process as ids not available
            skip = False

    if not skip:
        progress.start()
        for category in pc.unique(table[COL_NAMES[Cols.RecipeCategory]]):
            if not category:
                continue

            new_id = insert_content(
                curs, CATEGORY_FIELDS, (category, ), CATEGORY_TABLE,
                unique=True)
            categories[str(category)] = \
                new_id or \
                get_content_id(curs, CATEGORY_TABLE, CATEGORY_NAME, category)

            progress.inc(new_id)

        pickle_file = pickle_data(CATEGORY_TABLE, categories, folder)

        progress.end(f'pickled data to {pickle_file}')


    # process keywords
    process_list(args, curs, progress, 'Keyword', KEYWORD_TABLE,
                 KEYWORD_FIELDS, table[COL_NAMES[Cols.Keywords]],
                 keywords, args.skip_keyword, folder)

    # process ingredients
    curs.execute(
        f'SELECT id FROM {MEASURE_TABLE} WHERE "{MEASURE_NAME}" = %s',
        ('unit',))
    unit_id = curs.fetchone()[0]

    process_list(args, curs, progress, 'Ingredient', INGREDIENT_TABLE,
                 INGREDIENT_FIELDS,
                 table[COL_NAMES[Cols.RecipeIngredientParts]],
                 ingredients, args.skip_ingredient, folder,
                 values_func=lambda val: (val, unit_id))

    # process authors


    # process recipes

    # process images
    # process_list(args, curs, progress, 'Image', IMAGE_TABLE, IMAGE_FIELDS, table[COL_NAMES[Cols.Images]], keywords,
    #              args.skip_pictures, folder)


class Progress:
    """ Progress indicator class """
    title: str
    tick: int
    table: str
    processed: int
    added: int
    size: int

    LEAD: str = 'Processing '

    def __init__(self, title: str, tick: int, table: str):
        self.reset(title, tick, table)

    def reset(self, title: str, tick: int, table: str):
        """ Reset progress object """
        self.title = title
        self.tick = tick
        self.table = table
        self.processed = 0
        self.added = 0
        self.size = 0

    def start(self):
        """ Start progress object """
        self.processed = 0
        self.added = 0
        self.size = 0
        print(f'{self.title}: {Progress.LEAD}', end='', flush=True)

    def skip(self, msg: str = ''):
        """ Skip progress """
        self.processed = 0
        self.added = 0
        self.size = 0
        print(f'{self.title}: Skipped {msg}')

    def inc(self, new_id: Optional[int] = None, processed: int = 1,
            added: int = 1):
        """ Increment progress """
        self.processed += processed
        if new_id:
            self.added += added
        if self.processed % self.tick == 0:
            progress = f'{self.processed}'
            backspace = '\b' * self.size if self.size else ''
            self.size = len(progress)
            print(f'{backspace}{progress}', end='', flush=True)

    def end(self, msg: str = ''):
        """ Progress completed """
        backspace = '\b' * (self.size + len(Progress.LEAD)) if self.size else ''
        print(f'{backspace}Processed {self.processed} entries for '
              f'{self.table}, adding {self.added} new entries')
        if msg:
            indent = ' ' * (len(f'{self.title}: '))
            print(f'{indent}{msg}')


def process_list(args: argparse.Namespace, curs, progress: Progress,
                 title: str, table_name: str, fields: list[str],
                 parquet_col, cache: dict, skip: bool, folder: str,
                 values_func: Optional[Callable[[str], tuple]] = None,
                 get_field: str = None):
    """
    Process a list
    :param args: program arguments
    :param curs: cursor
    :param progress: progress instance
    :param title: progress title
    :param table_name: name of table to update
    :param fields: fields list
    :param parquet_col: data from parquet source
    :param cache: cache dict to store info
    :param skip: skip flag
    :param folder: path to data folder
    :param values_func: function to generate vales to store in database
    :param get_field: field to use to get id of inserted row;
                    default first field in `fields`
    """
    if get_field is None:
        get_field = fields[0]   # default to first field
    if values_func is None:
        def one_val_tuple(val):
            return val,
        values_func = one_val_tuple

    progress.reset(title, args.progress, table_name)
    if skip:
        data, pickle_file = unpickle_data(table_name, folder)
        if data:
            cache.update(data)

            progress.skip(f'- read ids from {pickle_file}')
        else:
            # need to process as ids not available
            skip = False

    if not skip:
        progress.start()
        for words in parquet_col:
            if not words:
                continue

            for word in words.as_py():
                if not word:
                    continue

                new_id = insert_content(
                    curs, fields, values_func(word), table_name, unique=True)
                cache[str(word)] = \
                    new_id or \
                    get_content_id(curs, table_name, get_field, word)
                progress.inc(new_id)

        pickle_file = pickle_data(table_name, cache, folder)

        progress.end(f'pickled data to {pickle_file}')


def pickle_file_name(table_name: str) -> str:
    """ Generate name of pickle file """
    return f'{table_name}.pickle'


def unpickle_data(table_name: str, folder: str) -> tuple[Optional[dict], str]:
    """
    Unpickle a data file
    :param table_name: database table name
    :param folder: data folder
    :return: tuple of unpickled dara and pickle file name
    """
    data = None
    pickle_file = os.path.join(folder, pickle_file_name(table_name))

    if os.path.exists(pickle_file):
        # pickle exists so read it
        with open(pickle_file, 'rb') as file:
            # The protocol version used is detected automatically, so we do not
            # have to specify it.
            data = pickle.load(file)

    return data, pickle_file


def pickle_data(table_name: str, data: dict, folder:str) -> str:
    """
    Pickle a data file
    :param table_name: database table name
    :param data: data to pickle
    :param folder: data folder
    :return: pickle file name
    """
    pickle_file = os.path.join(folder, pickle_file_name(table_name))
    with open(pickle_file, 'wb') as file:
        # Pickle the 'data' dictionary using the highest protocol
        # available.
        pickle.dump(data, file, pickle.HIGHEST_PROTOCOL)

    return pickle_file
