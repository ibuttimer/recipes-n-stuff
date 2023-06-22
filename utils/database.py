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
from django.db import connection


def table_exists(name: str) -> bool:
    """
    Check if the specified table exists in the database
    :param name: name of table
    :return: True if table exists
    """
    all_tables = connection.introspection.table_names()
    return name.lower() in all_tables


class AppRouter:
    """
    A router to control all database operations.
    """

    db_name: str = None     # migration db name

    def db_for_read(self, model, **hints):
        """
        Always read from migration db if set
        """
        return self.db_name if self.db_name is not None else model.objects.db

    def db_for_write(self, model, **hints):
        """
        Write to models db.
        """
        return model.objects.db

    def allow_relation(self, obj1, obj2, **hints):
        """
        Always allow relations.
        """
        return True

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Always allow migrations.
        """
        if self.db_name is None:
            self.db_name = db
        return True
