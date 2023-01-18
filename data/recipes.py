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
from typing import Optional, Callable, Union, Tuple, Any
import random
import string
from collections import namedtuple
from datetime import datetime, MINYEAR, timezone

import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.parquet as pq
import numpy as np
from argon2 import PasswordHasher
from pyarrow import StringScalar

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

# password generation
PASSWORD_CHARS = string.ascii_letters + string.digits + "!£$&*@#?%^=+-/~.,:;"
PASSWORD_LEN = 10
ph = PasswordHasher()

# recipe categories
CATEGORY_TABLE = 'recipes_category'
CATEGORY_NAME = 'name'
CATEGORY_FIELDS = [CATEGORY_NAME]
# recipe keywords
KEYWORD_TABLE = 'recipes_keyword'
KEYWORD_NAME = 'name'
KEYWORD_FIELDS = [KEYWORD_NAME]
# recipe measures
MEASURE_TABLE = 'recipes_measure'
MEASURE_NAME = 'name'
# recipe ingredients
INGREDIENT_TABLE = 'recipes_ingredient'
INGREDIENT_NAME = 'name'
INGREDIENT_MEASURE = 'measure_id'
INGREDIENT_FIELDS = [INGREDIENT_NAME, INGREDIENT_MEASURE]
# recipe authors
AUTHOR_TABLE = 'user_user'
AUTHOR_FIRST_NAME = 'first_name'
AUTHOR_LAST_NAME = 'last_name'
AUTHOR_USERNAME = 'username'
AUTHOR_PASSWORD = 'password'
AUTHOR_EMAIL = 'email'
AUTHOR_IS_SUPERUSER = 'is_superuser'
AUTHOR_IS_STAFF = 'is_staff'
AUTHOR_IS_ACTIVE = 'is_active'
AUTHOR_DATE_JOINED = 'date_joined'
AUTHOR_BIO = 'bio'
AUTHOR_AVATAR = 'avatar'
AUTHOR_FIELDS = [
    AUTHOR_FIRST_NAME, AUTHOR_LAST_NAME, AUTHOR_USERNAME, AUTHOR_PASSWORD,
    AUTHOR_EMAIL, AUTHOR_IS_SUPERUSER, AUTHOR_IS_STAFF, AUTHOR_IS_ACTIVE,
    AUTHOR_DATE_JOINED, AUTHOR_BIO, AUTHOR_AVATAR
]
Author = namedtuple("Author", ["food_id", "new_id"])
YEAR_DOT = datetime(MINYEAR, 1, 1, tzinfo=timezone.utc)
AVATAR_BLANK = 'avatar_blank'
# recipe images
IMAGE_TABLE = 'recipes_image'
IMAGE_NAME = 'name'
IMAGE_FIELDS = [IMAGE_NAME]

categories = {}     # key: category, val: id
keywords = {}       # key: keyword, val: id
ingredients = {}    # key: name, val: id
authors = {}        # key: username, val: namedtuple Author


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
    process_data(args, curs, progress, 'Keyword', KEYWORD_TABLE,
                 KEYWORD_FIELDS, table[COL_NAMES[Cols.Keywords]],
                 keywords, args.skip_keyword, folder)

    # process ingredients
    curs.execute(
        f'SELECT id FROM {MEASURE_TABLE} WHERE "{MEASURE_NAME}" = %s',
        ('unit',))
    unit_id = curs.fetchone()[0]

    process_data(args, curs, progress, 'Ingredient', INGREDIENT_TABLE,
                 INGREDIENT_FIELDS,
                 table[COL_NAMES[Cols.RecipeIngredientParts]],
                 ingredients, args.skip_ingredient, folder,
                 values_func=lambda val: (val, unit_id))

    # process authors
    def user_values(author_name: Union[str, StringScalar])\
            -> tuple[str, str, str | StringScalar, str, str, bool, bool,
            bool, datetime, str, str]:
        """ Generate user values """
        # Note: password is a random hashed value as the user will never login
        splits = str(author_name).split()
        # same order as AUTHOR_FIELDS
        return splits[0], ' '.join(splits[1:]) if len(splits) > 1 else '', \
            author_name, get_random_password(), '', False, False, False, \
            YEAR_DOT, 'Imported from kaggle dataset', AVATAR_BLANK

    user_table = None
    def get_user_table():
        """ Get the user data """
        nonlocal user_table
        # only generate unique user table if required, it takes a while
        user_table = drop_duplicates(pa.table([
            table[COL_NAMES[Cols.AuthorName]],
            table[COL_NAMES[Cols.AuthorId]]
        ], names=[COL_NAMES[Cols.AuthorName], COL_NAMES[Cols.AuthorId]]),
            COL_NAMES[Cols.AuthorName])
        return user_table[COL_NAMES[Cols.AuthorName]]

    def cache_user(id_cache: dict, key: Any, db_id: int, row: int) -> None:
        """
        Cache user info
        :param id_cache: cache to update
        :param key: username as key
        :param db_id: database id
        :param row: data row number
        """
        id_cache[str(key)] = Author(
            food_id=user_table[COL_NAMES[Cols.AuthorId]][row].as_py(),
            new_id=db_id)

    process_data(args, curs, progress, 'Author', AUTHOR_TABLE,
                 AUTHOR_FIELDS, get_user_table,
                 authors, args.skip_author, folder,
                 are_lists=False,
                 values_func=user_values, cache_func=cache_user)


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


def process_data(args: argparse.Namespace, curs, progress: Progress,
                 title: str, table_name: str, fields: list[str],
                 parquet_data: Union[Callable[[], Any], pa.Table, pa.Array],
                 cache: dict, skip: bool,
                 folder: Union[str, Path],
                 are_lists: bool = True,
                 values_func: Optional[Callable[[str], tuple]] = None,
                 cache_func: Optional[
                     Callable[[dict, Any, int, int], None]] = None,
                 get_field: str = None):
    """
    Process data
    :param args: program arguments
    :param curs: cursor
    :param progress: progress instance
    :param title: progress title
    :param table_name: name of table to update
    :param fields: fields list
    :param parquet_data: data from parquet source or callable to retrieve data
    :param cache: cache dict to store info
    :param skip: skip flag
    :param folder: path to data folder
    :param are_lists: values are lists flag; default True
    :param values_func: function to generate values to store in database
    :param cache_func: function to cache new entries;
                default key: read value, value: id of new entry
    :param get_field: field to use to get id of inserted row;
                    default first field in `fields`
    """
    if get_field is None:
        get_field = fields[0]   # default to first field
    if values_func is None:
        # default single value tuple
        values_func = one_val_tuple
    if cache_func is None:
        # default single value tuple
        def cache_key_id(id_cache: dict, key: Any, db_id: int,
                         row: int) -> None:
            """
            Cache key and database id
            :param id_cache: cache to update
            :param key: cache key
            :param db_id: database id
            :param row: data row number
            """
            id_cache[str(key)] = \
                db_id or \
                get_content_id(curs, table_name, get_field, key)
        cache_func = cache_key_id

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

        if isinstance(parquet_data, Callable):
            # do here so console has updated progress
            parquet_data = parquet_data()

        for row, words in enumerate(parquet_data):
            if not words:
                continue

            entries = words.as_py() if are_lists else [words]
            for word in entries:
                if not word:
                    continue

                new_id = insert_content(
                    curs, fields, values_func(word), table_name, unique=True)
                cache_func(cache, word, new_id, row)

                progress.inc(new_id)

        pickle_file = pickle_data(table_name, cache, folder)

        progress.end(f'pickled data to {pickle_file}')


def pickle_file_name(table_name: str) -> str:
    """ Generate name of pickle file """
    return f'{table_name}.pickle'


def unpickle_data(table_name: str,
                  folder: Union[str, Path]) -> tuple[Optional[dict], str]:
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


def pickle_data(table_name: str, data: dict, folder: Union[str, Path]) -> str:
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

def one_val_tuple(val) -> tuple:
    """
    Generate a tuple from a single value
    :param val: value
    :return: tuple
    """
    return val,


def get_random_password(length: int = PASSWORD_LEN) -> str:
    """ Generate a hashed random password """
    return ph.hash(
        ''.join(random.choice(PASSWORD_CHARS) for _ in range(length))
    )


def drop_duplicates(table: pa.Table, column_name: str) -> pa.Table:
    """
    Drop duplicate rows from a table based on unique values of a column

    [Taken from https://stackoverflow.com/a/66711534/4054609 by
     https://stackoverflow.com/users/13076586/christine]

    :param table: table to filter
    :param column_name: column name for unique values
    :return: filtered table
    """
    unique_values = pc.unique(table[column_name])
    unique_indices = [pc.index(table[column_name], value).as_py() for value in unique_values]
    mask = np.full((len(table)), False)
    mask[unique_indices] = True
    return table.filter(mask=mask)