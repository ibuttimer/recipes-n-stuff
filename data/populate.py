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
from pathlib import Path
import re
import csv
import argparse
from string import capwords

import environ
import psycopg2
from django.conf import settings
from django_countries import countries

from recipesnstuff import settings as app_settings
from data.recipes import load_recipe, DEFAULT_LOAD_COUNT
from data.data_utils import insert_content, get_content_id, Progress

# project folder
BASE_DIR = Path(__file__).resolve().parent.parent

if not settings.configured:
    # need to init django to get access to django_countries
    settings.configure(app_settings, DEBUG=True)

COUNTRYINFO_TABLE = 'profiles_countryinfo'
COUNTRYINFO_COUNTRY_COL = 'country'             # country column
COUNTRYINFO_SUBDIVISION_COL = 'subdivision'     # subdivision column

# subdivisions csv
COUNTRYINFO_TSV = 'subdivisions.txt'
# subdivisions csv columns
COUNTRYINFO_CODE = 0
COUNTRYINFO_NAME = 1
COUNTRYINFO_SUBDIVISION = 2
COUNTRYINFO_NUM_COLS = 3
# char used to separate multiple subdivisions, e.g. 'city/region'
MULTI_SUBDIV_SEP = '/'
# char used to indicate no subdivisions
NO_SUBDIV = '-'


CURRENCY_TABLE = 'checkout_currency'
CURRENCY_CODE_COL = 'code'              # currency code column
CURRENCY_NUMERIC_COL = 'numeric_code'   # currency numeric code column
CURRENCY_DIGITS_COL = 'digits'          # currency num of digits column
CURRENCY_NAME_COL = 'name'              # currency name column
CURRENCY_SYMBOL_COL = 'symbol'          # currency symbol column
CURRENCY_FIELDS = [
    CURRENCY_CODE_COL, CURRENCY_NUMERIC_COL, CURRENCY_DIGITS_COL,
    CURRENCY_NAME_COL, CURRENCY_SYMBOL_COL
]

# currency csv
CURRENCY_CSV = 'currency.csv'
STRIPE_SUPPORT_TXT = 'stripe_support.txt'
# currency csv columns
CURRENCY_CODE = 0
CURRENCY_NUMERIC_CODE = 1
CURRENCY_DIGITS = 2
CURRENCY_NAME = 3
CURRENCY_SYMBOL = 4
CURRENCY_NUM_COLS = 5
# char used to indicate not supported by Amex
NO_AMEX = '*'
GENERIC_CURRENCY_SYMBOL = '¤'


DEFAULT_HOST = 'http://127.0.0.1:8000/'
DEFAULT_DATA_FOLDER = 'data'
DEFAULT_ENV_FILE = '.env'
DEFAULT_DB_VAR = 'DATABASE_URL'
DEFAULT_PROGRESS = 150


def parse_args():
    parser = argparse.ArgumentParser(
        prog='populate',
        description='Populate database with standard data')
    parser.add_argument('-f', '--data_folder',
                        help=f'Path to data folder; '
                             f'default {DEFAULT_DATA_FOLDER}',
                        default=DEFAULT_DATA_FOLDER)
    parser.add_argument('-ef', '--env_file',
                        help=f'Path to the environment file; '
                             f'default {DEFAULT_ENV_FILE}',
                        default=DEFAULT_ENV_FILE)
    parser.add_argument('-dv', '--db_var',
                        help=f'Name of environment variable containing '
                             f'database connection string; '
                             f'default {DEFAULT_DB_VAR}',
                        default=DEFAULT_DB_VAR)
    parser.add_argument('-u', '--host',
                        help=f'Host url e.g. {DEFAULT_HOST}',
                        default=DEFAULT_HOST)
    parser.add_argument('-a', '--all', action='store_true',
                        help='Load all data',
                        default=False)
    parser.add_argument('-c', '--country', action='store_true',
                        help='Load country data',
                        default=False)
    parser.add_argument('-cc', '--currency', action='store_true',
                        help='Load currency data',
                        default=False)
    parser.add_argument('-r', '--recipe', action='store_true',
                        help='Load recipe data',
                        default=False)
    parser.add_argument('-sc', '--skip_category', action='store_true',
                        help='Skip categories during recipe data load',
                        default=False)
    parser.add_argument('-sk', '--skip_keyword', action='store_true',
                        help='Skip keywords during recipe data load',
                        default=False)
    parser.add_argument('-si', '--skip_ingredient', action='store_true',
                        help='Skip ingredients during recipe data load',
                        default=False)
    parser.add_argument('-sa', '--skip_author', action='store_true',
                        help='Skip authors during recipe data load',
                        default=False)
    parser.add_argument('-sr', '--skip_recipe', action='store_true',
                        help='Skip recipes during recipe data load',
                        default=False)
    parser.add_argument('-sl', '--skip_ingredient_list', action='store_true',
                        help='Skip ingredients list during recipe data load',
                        default=False)
    parser.add_argument('-sx', '--skip_keyword_list', action='store_true',
                        help='Skip recipe keywords list during recipe data '
                             'load',
                        default=False)
    parser.add_argument('-sd', '--skip_instruction_list',
                        action='store_true',
                        help='Skip recipe instructions list during recipe '
                             'data load',
                        default=False)
    parser.add_argument('-sp', '--skip_pictures', action='store_true',
                        help='Skip pictures during recipe data load',
                        default=False)
    parser.add_argument('-p', '--progress', type=int,
                        help=f'Progress indicator rate; '
                             f'default {DEFAULT_PROGRESS}',
                        default=DEFAULT_PROGRESS)
    parser.add_argument('-rc', '--recipe_count', type=int,
                        help='Max number of recipes to load; default all',
                        default=DEFAULT_LOAD_COUNT)
    args = parser.parse_args()
    return args


def process():
    args = parse_args()

    env = environ.Env()
    # Take environment variables from env file
    os.environ.setdefault('ENV_FILE', DEFAULT_ENV_FILE)
    os.environ.setdefault('SB_HOST', DEFAULT_HOST)
    environ.Env.read_env(
        os.path.join(
            BASE_DIR, args.env_file if args.env_file != DEFAULT_ENV_FILE else
            env('ENV_FILE')), overwrite=True
    )

    db_url = env(args.db_var)

    # ElephantSQL db names are chars, passwords can contain - and _
    regex = re.compile(
        rf'.*://(\w+):([\w_-]+)@([\w.]+)/(\w+).*', re.IGNORECASE)
    match = regex.match(db_url)
    if not match:
        print("Credentials not found. Did you set the env_file?")
        sys.exit(1)

    db_name = match.group(4)
    db_user = match.group(1)
    db_host = match.group(3)
    db_password = match.group(2)

    connection = f"dbname='{db_name}' user='{db_user}' host='{db_host}' " \
                 f"password='{db_password}'"
    with psycopg2.connect(connection) as conn:
        with conn.cursor() as curs:
            # load country
            if args.all or args.country:
                load_country(args, curs)
            # load currency
            if args.all or args.currency:
                load_currency(args, curs)
            # load recipes
            if args.all or args.recipe:
                load_recipe(args, curs)


def load_country(args: argparse.Namespace, curs):
    """
    Load country data
    :param args: program arguments
    :param curs: cursor
    """
    folder = Path(args.data_folder).resolve()
    filepath = os.path.join(folder, COUNTRYINFO_TSV)

    with open(filepath, encoding='utf-8') as csvfile:
        existing = 0
        added = 0
        # use | as quote char to avoid messing with " inside quotes
        country_reader = csv.reader(
            csvfile, delimiter='\t', quotechar='|')
        for row in country_reader:
            if not row or row[0].startswith('#'):
                # skip comments and empty lines
                continue
            if len(row) != COUNTRYINFO_NUM_COLS:
                raise ValueError(f'Unexpected length: {row}')

            row[COUNTRYINFO_CODE] = row[COUNTRYINFO_CODE].upper()
            row[COUNTRYINFO_SUBDIVISION] = \
                capwords(row[COUNTRYINFO_SUBDIVISION],
                         sep=MULTI_SUBDIV_SEP)
            if row[COUNTRYINFO_CODE] not in countries.alt_codes:
                # skip unrecognised country codes
                continue

            content = get_content_id(
                curs, COUNTRYINFO_TABLE, COUNTRYINFO_COUNTRY_COL,
                row[COUNTRYINFO_CODE])
            if content:
                existing += 1
            else:
                save_countryinfo(
                    curs, row[COUNTRYINFO_CODE],
                    row[COUNTRYINFO_SUBDIVISION])
                added += 1

    print(f'Country: Added {added} entries to {COUNTRYINFO_TABLE}, '
          f'skipped {existing} entries')


def save_countryinfo(curs, country: str, subdivision: str) -> int:
    """
    Save country info
    :param curs: cursor
    :param country: country code
    :param subdivision: subdivision name
    """
    values = (
        country,        # country code
        subdivision if subdivision != NO_SUBDIV else '',    # subdivision
    )

    fields = [
        COUNTRYINFO_COUNTRY_COL, COUNTRYINFO_SUBDIVISION_COL
    ]
    result = insert_content(curs, fields, values, COUNTRYINFO_TABLE)

    return result


def load_currency(args: argparse.Namespace, curs):
    """
    Load currency data
    :param args: program arguments
    :param curs: cursor
    """
    folder = Path(args.data_folder).resolve()
    currency_path = os.path.join(folder, CURRENCY_CSV)
    stripe_path = os.path.join(folder, STRIPE_SUPPORT_TXT)

    progress = Progress('Currency', args.progress, CURRENCY_TABLE)
    progress.start()

    # load stripe supported list
    currency_set = set()
    with open(stripe_path, encoding='utf-8') as stripe_file:
        for row in stripe_file:
            row = row.strip()
            if row.startswith('#'):
                # skip comments and empty lines
                continue

            code = row[:-1] if row.endswith(NO_AMEX) else row
            currency_set.add(code.upper())

    # load currency list
    with open(currency_path, encoding='utf-8') as csvfile:
        existing = 0
        added = 0
        # use | as quote char to avoid messing with " inside quotes
        currency_reader = csv.reader(
            csvfile, delimiter=',', quotechar='|')
        for row in currency_reader:
            if not row or row[0].startswith('#'):
                # skip comments and empty lines
                continue
            if len(row) != CURRENCY_NUM_COLS:
                raise ValueError(f'Unexpected length: {row}')

            row[CURRENCY_CODE] = row[CURRENCY_CODE].upper()
            if row[COUNTRYINFO_CODE] not in currency_set:
                # skip unsupported currencies
                continue
            for idx in [CURRENCY_NUMERIC_CODE, CURRENCY_DIGITS]:
                row[idx] = int(row[idx])

            content = get_content_id(
                curs, CURRENCY_TABLE, CURRENCY_NAME_COL,
                row[CURRENCY_NAME])
            if content:
                existing += 1
            else:
                values = tuple([
                    row[idx] for idx in range(CURRENCY_NUM_COLS)
                ])

                new_id = insert_content(
                    curs, CURRENCY_FIELDS, values, CURRENCY_TABLE, unique=True
                )
                added += 1

                progress.inc(new_id)

    progress.end()


if __name__ == "__main__":
    process()
