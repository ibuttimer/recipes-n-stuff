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

from pathlib import Path
from typing import Any, Optional

from psycopg2.extras import execute_batch

# project folder
BASE_DIR = Path(__file__).resolve().parent.parent


def insert_content(curs, fields: list[str], values: tuple, table: str,
                   unique: bool = False,
                   seek_field: str = None, seek_value: str = None):
    """
    Insert content into database
    :param curs: cursor
    :param fields: list of fields
    :param values: list of values
    :param table: table in insert into
    :param unique: entry is unique flag: default False
    :param seek_field: field to use to load inserted entry; default None
    :param seek_value: value to use to load inserted entry; default None
    """
    values_fmt = ','.join(['%s' for _ in range(len(values))])
    field_list = ', '.join(fields)

    sql = f"INSERT INTO {table} ({field_list}) " \
          f"VALUES ({values_fmt});" \
          if not unique else \
          f"INSERT INTO {table} ({field_list}) " \
          f"SELECT {vals(values)} WHERE NOT EXISTS (" \
          f"SELECT NULL FROM {table} " \
          f"WHERE ({field_list}) = ({values_fmt})) RETURNING id"
    curs.execute(sql, tuple([
        str(val) for val in values
    ]))
    new_id = curs.fetchone()[0] if curs.rowcount else None

    # get id of new content
    if not new_id and seek_field and seek_value:
        new_id = get_content_id(
            curs, table, seek_field, seek_value, exception=True)

    return new_id


def single_quote_safe(val: Any):
    """ Make a single quote safe value"""
    return str(val).replace("'", "''").replace("%", "%%")


def vals(data: list):
    """ Join a list of values """
    return ', '.join([
        f"'{single_quote_safe(val)}'" for val in data
    ])


def get_content_id(curs, table: str, seek_field: str, seek_value: str,
                   ignore_case: bool = True, exception: bool = False
                   ) -> Optional[int]:
    """
    Get the is of a database entry
    :param curs: cursor
    :param table: table to search
    :param seek_field: field to use to load entry
    :param seek_value: value to use to load entry
    :param ignore_case: ignore case flag; default True
    :param exception: raise exception flag; default False
    :return: content id
    """
    if ignore_case:
        seek_field = f"LOWER({seek_field})"
        seek_value = f"LOWER('{single_quote_safe(seek_value)}')"
    curs.execute(f"SELECT id FROM {table} WHERE "
                 f"{seek_field}={seek_value};")
    content = curs.fetchone()
    if not content and exception:
        raise ValueError(f"Content {seek_field}={seek_value} not found")
    return content[0] if content else None


def insert_batch(curs, fields: str, values: tuple, table: str):
    """
    Perform a batch insert
    :param curs: cursor
    :param fields: fields list
    :param values: values to insert
    :param table: table to insert into
    """
    execute_batch(curs, f"INSERT INTO {table} ({fields}) VALUES (%s)", values)
