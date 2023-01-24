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
from typing import Optional, Callable, Union, Any
import random
import string
from collections import namedtuple
from datetime import datetime, MINYEAR, timezone, timedelta

import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.parquet as pq
import numpy as np
from argon2 import PasswordHasher
from pyarrow import StringScalar
from isoduration import parse_duration

from data.data_utils import (
    insert_content, get_content_id, Progress, insert_batch, DEFAULT_PAGE_SIZE
)

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
    Note: Must be same order as COL_NAMES
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

    @staticmethod
    def float_fields():
        """ Field using float """
        return [
            Cols.Calories, Cols.FatContent, Cols.SaturatedFatContent,
            Cols.CholesterolContent, Cols.SodiumContent,
            Cols.CarbohydrateContent, Cols.FiberContent, Cols.SugarContent,
            Cols.ProteinContent
        ]

    @staticmethod
    def int_fields():
        """ Field using float """
        return [Cols.RecipeId, Cols.RecipeServings]


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
# keywords instructions list
RECIPE_KEYWORDS_TABLE = 'recipes_recipe_keywords'
RECIPE_KEYWORDS_RECIPE_ID = 'recipe_id'
RECIPE_KEYWORDS_KEYWORD_ID = 'keyword_id'
RECIPE_KEYWORDS_FIELDS = [
    RECIPE_KEYWORDS_RECIPE_ID, RECIPE_KEYWORDS_KEYWORD_ID,
]
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
# recipe info
RECIPE_TABLE = 'recipes_recipe'
RECIPE_NAME = 'name'
RECIPE_FOOD_ID = 'food_id'
RECIPE_PREP_TIME = 'prep_time'
RECIPE_COOK_TIME = 'cook_time'
RECIPE_DATE_PUBLISHED = 'date_published'
RECIPE_DESCRIPTION = 'description'
RECIPE_SERVINGS = 'servings'
RECIPE_RECIPE_YIELD = 'recipe_yield'
RECIPE_CALORIES = 'calories'
RECIPE_FAT_CONTENT = 'fat_content'
RECIPE_SATURATED_FAT_CONTENT = 'saturated_fat_content'
RECIPE_CHOLESTEROL_CONTENT = 'cholesterol_content'
RECIPE_SODIUM_CONTENT = 'sodium_content'
RECIPE_CARBOHYDRATE_CONTENT = 'carbohydrate_content'
RECIPE_FIBRE_CONTENT = 'fibre_content'
RECIPE_SUGAR_CONTENT = 'sugar_content'
RECIPE_PROTEIN_CONTENT = 'protein_content'
RECIPE_AUTHOR = 'author_id'
RECIPE_CATEGORY = 'category_id'
RECIPE_FIELDS = [
    RECIPE_NAME,
    RECIPE_FOOD_ID,
    RECIPE_PREP_TIME,
    RECIPE_COOK_TIME,
    RECIPE_DATE_PUBLISHED,
    RECIPE_DESCRIPTION,
    RECIPE_SERVINGS, RECIPE_RECIPE_YIELD, RECIPE_CALORIES,
    RECIPE_FAT_CONTENT, RECIPE_SATURATED_FAT_CONTENT,
    RECIPE_CHOLESTEROL_CONTENT, RECIPE_SODIUM_CONTENT,
    RECIPE_CARBOHYDRATE_CONTENT, RECIPE_FIBRE_CONTENT,
    RECIPE_SUGAR_CONTENT, RECIPE_PROTEIN_CONTENT, RECIPE_AUTHOR,
    RECIPE_CATEGORY
]
RECIPE_COLS = {
    key: val for key, val in [
        (RECIPE_NAME, Cols.Name),
        (RECIPE_FOOD_ID, Cols.RecipeId),
        (RECIPE_PREP_TIME, Cols.PrepTime),
        (RECIPE_COOK_TIME, Cols.CookTime),
        (RECIPE_DATE_PUBLISHED, Cols.DatePublished),
        (RECIPE_DESCRIPTION, Cols.Description),
        (RECIPE_SERVINGS, Cols.RecipeServings),
        (RECIPE_RECIPE_YIELD, Cols.RecipeYield),
        (RECIPE_CALORIES, Cols.Calories),
        (RECIPE_FAT_CONTENT, Cols.FatContent),
        (RECIPE_SATURATED_FAT_CONTENT, Cols.SaturatedFatContent),
        (RECIPE_CHOLESTEROL_CONTENT, Cols.CholesterolContent),
        (RECIPE_SODIUM_CONTENT, Cols.SodiumContent),
        (RECIPE_CARBOHYDRATE_CONTENT, Cols.CarbohydrateContent),
        (RECIPE_FIBRE_CONTENT, Cols.FiberContent),
        (RECIPE_SUGAR_CONTENT, Cols.SugarContent),
        (RECIPE_PROTEIN_CONTENT, Cols.ProteinContent),
        (RECIPE_AUTHOR, Cols.AuthorName),
        (RECIPE_CATEGORY, Cols.RecipeCategory),
    ]
}
assert list(RECIPE_COLS.keys()) == RECIPE_FIELDS
# recipe ingredients list
RECIPE_INGREDIENT_TABLE = 'recipes_recipeingredient'
RECIPE_INGREDIENT_RECIPE_ID = 'recipe_id'
RECIPE_INGREDIENT_INGREDIENT_ID = 'ingredient_id'
RECIPE_INGREDIENT_QUANTITY = 'quantity'
RECIPE_INGREDIENT_FIELDS = [
    RECIPE_INGREDIENT_RECIPE_ID, RECIPE_INGREDIENT_INGREDIENT_ID,
    RECIPE_INGREDIENT_QUANTITY
]
# recipe instructions
INSTRUCTION_TABLE = 'recipes_instruction'
INSTRUCTION_TEXT = 'text'
INSTRUCTION_FIELDS = [INSTRUCTION_TEXT]
# recipe instructions list
RECIPE_INSTRUCTIONS_TABLE = 'recipes_recipe_instructions'
RECIPE_INSTRUCTIONS_RECIPE_ID = 'recipe_id'
RECIPE_INSTRUCTIONS_INSTRUCTION_ID = 'instruction_id'
RECIPE_INSTRUCTIONS_FIELDS = [
    RECIPE_INSTRUCTIONS_RECIPE_ID, RECIPE_INSTRUCTIONS_INSTRUCTION_ID,
]
# recipe images
IMAGE_TABLE = 'recipes_image'
IMAGE_NAME = 'name'
IMAGE_FIELDS = [IMAGE_NAME]

categories = {}     # key: category, val: id
keywords = {}       # key: food.com id, val: list of instruction ids
ingredients = {}    # key: name, val: id
authors = {}        # key: username, val: namedtuple Author
recipes = {}        # key: food.com id, val: id
instructions = {}   # key: food.com id, val: list of instruction ids


def load_recipe(args: argparse.Namespace, curs):
    """
    Load recipe data
    :param args: program arguments
    :param curs: cursor
    """
    # load recipe info
    folder = Path(args.data_folder).resolve()
    filepath = os.path.join(folder, RECIPES_PARQUET)

    # recipe table
    raw_table = pq.read_table(filepath)

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
        for category in pc.unique(raw_table[COL_NAMES[Cols.RecipeCategory]]):
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

    # process ingredients
    curs.execute(
        f'SELECT id FROM {MEASURE_TABLE} WHERE "{MEASURE_NAME}" = %s',
        ('unit',))
    unit_id = curs.fetchone()[0]

    table_fields = ', '.join(INGREDIENT_FIELDS)
    process_data(
        args, curs, progress, 'Ingredient', INGREDIENT_TABLE, table_fields,
        raw_table[COL_NAMES[Cols.RecipeIngredientParts]], args.skip_ingredient,
        folder, values_func=lambda val, row, idx: (val, unit_id),
        cache=ingredients)

    # process authors
    def user_values(
            author_name: Union[str, StringScalar], row: int) -> tuple:
        """ Generate user values """
        # Note: password is a random hashed value as the user will never login
        splits = str(author_name).split()
        # same order as AUTHOR_FIELDS
        return splits[0], ' '.join(splits[1:]) if len(splits) > 1 else '', \
            author_name, get_random_password(), '', False, False, False, \
            YEAR_DOT, 'Imported from kaggle dataset', AVATAR_BLANK

    user_table: Optional[pa.Table] = None

    def get_user_table():
        """ Get the user data """
        nonlocal user_table
        # only generate unique user table if required, it takes a while
        user_table = drop_duplicates(pa.table([
            raw_table[COL_NAMES[Cols.AuthorName]],
            raw_table[COL_NAMES[Cols.AuthorId]]
        ], names=[COL_NAMES[Cols.AuthorName], COL_NAMES[Cols.AuthorId]]),
            COL_NAMES[Cols.AuthorName])
        return user_table[COL_NAMES[Cols.AuthorName]]

    def cache_user(
            id_cache: dict, key: Any, db_id: int, row: int, *args) -> None:
        """
        Cache user info
        :param id_cache: cache to update
        :param key: username as key
        :param db_id: database id
        :param row: data row number
        """
        if id_cache is not None:
            id_cache[str(key)] = Author(
                food_id=user_table[COL_NAMES[Cols.AuthorId]][row].as_py(),
                new_id=db_id)

    table_fields = ', '.join(AUTHOR_FIELDS)
    process_data(
        args, curs, progress, 'Author', AUTHOR_TABLE, table_fields,
        get_user_table, args.skip_author, folder, are_lists=False,
        values_func=user_values, cache=authors, cache_func=cache_user)

    # process recipes
    def recipe_check(recipe_id: Any, row: int) -> bool:
        """ Check ok to add recipe """
        # length of recipe ingredients and quantities sometimes don't match,
        # e.g. "1/2 cup butter or 1/2 cup margarine", only the butter will be
        # in the quantities list, or
        # if they don't have a link to an 'about' for the ingredient it won't
        # appear in the ingredients list
        # skip those as no way to generate a full list easily
        ingredient_list = raw_table[
            COL_NAMES[Cols.RecipeIngredientParts]][row].as_py()
        quantities = raw_table[
            COL_NAMES[Cols.RecipeIngredientQuantities]][row].as_py()
        return len(ingredient_list) == len(quantities)

    def recipe_values(
            recipe_id: Union[str, StringScalar], row: int, idx: int) -> tuple:
        """ Generate recipe values """
        # same order as RECIPE_FIELDS
        values = []
        for _, col in RECIPE_COLS.items():
            value = raw_table[COL_NAMES[col]][row].as_py()
            if col in [Cols.PrepTime, Cols.CookTime]:
                # pass
                if value:
                    duration = parse_duration(value)
                    value = timedelta(
                        days=float(duration.date.days),
                        minutes=float(duration.time.minutes),
                        hours=float(duration.time.hours))
                else:
                    value = timedelta()
            elif col == Cols.AuthorName:
                value = authors.get(value).new_id
            elif col == Cols.RecipeCategory:
                value = categories.get(value or 'None')
            elif col in Cols.int_fields():
                value = int(value) if value else 0
            values.append('' if value is None else value)

        return tuple(values)

    table_fields = ', '.join(RECIPE_FIELDS)
    process_data(
        args, curs, progress, 'Recipe', RECIPE_TABLE, table_fields,
        raw_table[COL_NAMES[Cols.RecipeId]], args.skip_recipe, folder,
        are_lists=False, values_func=recipe_values, cache=recipes,
        proceed_test=recipe_check)

    # save memory, clear no longer required caches
    categories.clear()
    authors.clear()

    # From here on only use 'recipes_table' NOT 'raw_table'

    # process keywords
    recipes_table: Optional[pa.Table] = None

    def get_recipes_table() -> pa.Table:
        """ Get the ingredients list data """
        nonlocal recipes_table

        if recipes_table is None:
            req_indices = [
                pc.index(
                    raw_table[COL_NAMES[Cols.RecipeId]], float(food_id)).as_py()
                for food_id in recipes
            ]
            mask = np.full((len(raw_table)), False)
            mask[req_indices] = True
            recipes_table = raw_table.filter(mask=mask)

        return recipes_table

    def cache_link_id(
            id_cache: dict, text: Any, db_id: int, row: int,
            idx: int, data_table: pa.Table) -> None:
        """
        Cache instruction info
        :param id_cache: cache to update
        :param text: instruction
        :param db_id: database id
        :param row: data row number
        :param idx: index within recipe instructions list
        :param data_table: parquet data table
        """
        if id_cache is not None:
            # key: food.com id, val: list of instruction ids
            food_id = data_table[COL_NAMES[Cols.RecipeId]][row].as_py()
            id_list = id_cache[food_id] if food_id in id_cache else []
            id_list.append(db_id)
            id_cache[food_id] = id_list

    def cache_keyword_id(
            id_cache: dict, text: Any, db_id: int, row: int,
            idx: int) -> None:
        """
        Cache keyword info
        :param id_cache: cache to update
        :param text: instruction
        :param db_id: database id
        :param row: data row number
        :param idx: index within recipe instructions list
        """
        cache_link_id(id_cache, text, db_id, row, idx, recipes_table)

    table_fields = ', '.join(KEYWORD_FIELDS)
    process_data(
        args, curs, progress, 'Keyword', KEYWORD_TABLE, table_fields,
        lambda : get_recipes_table()[COL_NAMES[Cols.Keywords]],
        args.skip_keyword, folder,
        cache=keywords, cache_func=cache_keyword_id)

    if not args.skip_keyword:
        table_fields = ', '.join(RECIPE_KEYWORDS_FIELDS)
        process_link_table(
            args, curs, progress, 'Link recipe keywords',
            RECIPE_KEYWORDS_TABLE, table_fields, keywords)

    # process recipe ingredients list
    ingredients_table: Optional[pa.Table] = None

    def get_ingredients_table():
        """ Get the ingredients list data """
        nonlocal ingredients_table

        recipe_table = get_recipes_table()

        ingredients_table = pa.table([
            recipe_table[COL_NAMES[Cols.RecipeId]],
            recipe_table[COL_NAMES[Cols.RecipeIngredientParts]],
            recipe_table[COL_NAMES[Cols.RecipeIngredientQuantities]],
            recipe_table[COL_NAMES[Cols.Name]]
        ], names=[
            COL_NAMES[Cols.RecipeId], COL_NAMES[Cols.RecipeIngredientParts],
            COL_NAMES[Cols.RecipeIngredientQuantities], COL_NAMES[Cols.Name]
        ])
        return ingredients_table[COL_NAMES[Cols.RecipeIngredientParts]]

    def ingredients_list_values(
            ingredient: Union[str, StringScalar], row: int,
            idx: int) -> tuple:
        """ Generate ingredients list values """
        # same order as RECIPE_INGREDIENT_FIELDS
        food_id = ingredients_table[
            COL_NAMES[Cols.RecipeId]][row].as_py()
        quantities = ingredients_table[
            COL_NAMES[Cols.RecipeIngredientQuantities]][row].as_py()
        # TODO keys for ingredients name/id cache
        # reprocess ingredients (takes long time) to verify fix for keys
        # starting with '2%' having a value of in the pickled dict, and remove
        # db this lookup
        ingredient_id = ingredients.get(str(ingredient))
        if ingredient_id is None:
            ingredient_id = get_content_id(
                curs, INGREDIENT_TABLE, INGREDIENT_NAME, str(ingredient))
            ingredients[str(ingredient)] = ingredient_id

        return tuple([
            recipes.get(str(food_id)),
            ingredients.get(str(ingredient)),
            quantities[idx] or '' if quantities else ''
        ])

    # TODO remove after 'keys for ingredients name/id cache' ok
    if not args.skip_ingredient_list:
        pickle_data(INGREDIENT_TABLE, ingredients, folder)

    table_fields = ', '.join(RECIPE_INGREDIENT_FIELDS)
    process_data(
        args, curs, progress, 'Ingredient lists', RECIPE_INGREDIENT_TABLE,
        table_fields, get_ingredients_table, args.skip_ingredient_list,
        folder, are_lists=True, values_func=ingredients_list_values)

    # save memory, clear no longer required caches
    ingredients.clear()

    # process recipe instructions

    def cache_instruction(
            id_cache: dict, text: Any, db_id: int, row: int,
            idx: int) -> None:
        """
        Cache instruction info
        :param id_cache: cache to update
        :param text: instruction
        :param db_id: database id
        :param row: data row number
        :param idx: index within recipe instructions list
        """
        cache_link_id(id_cache, text, db_id, row, idx, recipes_table)

    table_fields = ', '.join(INSTRUCTION_FIELDS)
    process_data(
        args, curs, progress, 'Instructions', INSTRUCTION_TABLE,
        table_fields,
        lambda : get_recipes_table()[COL_NAMES[Cols.RecipeInstructions]],
        args.skip_instruction_list, folder, unique=False, are_lists=True,
        cache=instructions, cache_func=cache_instruction)

    if not args.skip_instruction_list:
        table_fields = ', '.join(RECIPE_INSTRUCTIONS_FIELDS)
        process_link_table(
            args, curs, progress, 'Link recipe instructions',
            RECIPE_INSTRUCTIONS_TABLE, table_fields, instructions)



    # process recipe images
    # table_fields = ', '.join(IMAGE_FIELDS)
    # process_data(args, curs, progress, 'Image', IMAGE_TABLE, table_fields, recipes_table[COL_NAMES[Cols.Images]],
    #              args.skip_pictures, folder, are_lists=True)


def process_data(args: argparse.Namespace, curs, progress: Progress,
                 title: str, table_name: str, fields: Union[str, list[str]],
                 parquet_data: Union[Callable[[], Any], pa.Table, pa.Array],
                 skip: bool, folder: Union[str, Path], are_lists: bool = True,
                 batch_mode: bool = False, unique: bool = True,
                 values_func: Optional[
                     Callable[[Any, int, int], tuple]
                 ] = None, cache: dict = None,
                 cache_func: Optional[
                     Callable[[dict, Any, int, int, int], None]] = None,
                 proceed_test: Optional[
                        Callable[[Any, int], bool]
                 ] = None, get_field: str = None):
    """
    Process data
    :param args: program arguments
    :param curs: cursor
    :param progress: progress instance
    :param title: progress title
    :param table_name: name of table to update
    :param fields: fields list
    :param parquet_data: data from parquet source or callable to retrieve data
    :param skip: skip flag
    :param folder: path to data folder
    :param are_lists: values are lists flag; default True
    :param batch_mode: batch mode insert data to database: default = False
    :param unique: database is unique: default = True
    :param values_func: function to generate values to store in database
    :param cache: cache dict to store info; default None
    :param cache_func: function to cache new entries;
                default key: read value, value: id of new entry
    :param proceed_test: function to check if entry should be added;
                default None
    :param get_field: field to use to get id of inserted row;
                    default first field in `fields`
    """
    if values_func is None:
        # default single value tuple
        values_func = one_val_tuple
    if get_field is None:
        # default to first field
        get_field = fields[0] if isinstance(fields, list) \
            else fields.split(',')[0].strip()
    if cache_func is None:
        # default single value tuple
        def cache_key_id(id_cache: dict, key: Any, db_id: int, *args) -> None:
            """
            Cache key and database id
            :param id_cache: cache to update
            :param key: cache key
            :param db_id: database id
            :param row: data row number
            """
            if id_cache is not None:
                id_cache[str(key)] = \
                    db_id or \
                    get_content_id(curs, table_name, get_field, key)
        cache_func = cache_key_id

    progress.reset(title, args.progress, table_name)
    if skip:
        if cache is not None:
            data, pickle_file = unpickle_data(table_name, folder)
            if data:
                cache.update(data)

                progress.skip(f'- read ids from {pickle_file}')
            else:
                # need to process as ids not available
                skip = False
        else:
            progress.skip()

    if not skip:
        progress.start()

        if isinstance(parquet_data, Callable):
            # do here so console has updated progress
            parquet_data = parquet_data()

        batch = []

        # kwargs for insert_content()
        insert_seek = {
            'unique': unique
        }
        if unique:
            insert_seek['seek_field'] = get_field

        for row, words in enumerate(parquet_data):
            if not words:
                continue

            if proceed_test:
                # check if ok to add entry
                if not proceed_test(words, row):
                    continue

            entries = words.as_py() if are_lists else [words]
            for idx, word in enumerate(entries):
                if not word:
                    continue

                if batch_mode:
                    # batch mode, so insert batch
                    batch.append(values_func(word, row, idx))
                else:
                    # non batch mode, so insert individually

                    if unique:
                        insert_seek['seek_value'] = word

                    new_id = insert_content(
                        curs, fields, values_func(word, row, idx), table_name,
                        **insert_seek)
                    if cache is not None:
                        cache_func(cache, word, new_id, row, idx)

                    progress.inc(new_id)

            if len(batch) > 0:
                insert_batch(curs, fields, tuple(batch), table_name)
                added = len(batch)
                progress.inc(added, added=added)
                batch.clear()

        if cache is not None:
            pickle_file = pickle_data(table_name, cache, folder)
            msg = f'pickled data to {pickle_file}'
        else:
            msg = None

        progress.end(msg=msg)


def process_link_table(
        args: argparse.Namespace, curs, progress: Progress,
        title: str, table_name: str, fields: Union[str, list[str]],
        cache: dict):
    """
    Process a many-to-many link table
    :param args: program arguments
    :param curs: cursor
    :param progress: progress instance
    :param title: progress title
    :param table_name: name of table to update
    :param fields: fields list
    :param cache: cache dict with food.com id as key and list of link ids
                    as value
    """
    progress.reset(title, args.progress, table_name)
    progress.start()

    batch = []
    for food_id, to_link_ids in cache.items():
        if not to_link_ids:
            continue

        recipe_db_id = recipes.get(str(food_id))
        batch.extend([
            (recipe_db_id, link_id)
            for link_id in to_link_ids
        ])

        if len(batch) > DEFAULT_PAGE_SIZE:
            insert_batch(curs, fields, tuple(batch), table_name)

            progress.inc(processed=len(batch))
            batch.clear()

    if len(batch) > 0:
        insert_batch(curs, fields, tuple(batch), table_name)

        progress.inc(processed=len(batch))
        batch.clear()

    progress.end()


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


def one_val_tuple(val: Any, row: int, idx: int) -> tuple:
    """
    Generate a tuple from a single value
    :param val: value
    :param row: row index
    :param idx: list item index
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
    unique_indices = [
        pc.index(table[column_name], value).as_py() for value in unique_values
    ]
    mask = np.full((len(table)), False)
    mask[unique_indices] = True
    return table.filter(mask=mask)
