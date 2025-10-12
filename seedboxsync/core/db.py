# -*- coding: utf-8 -*-
#
# Copyright (C) 2015-2025 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#

import os
from peewee import SqliteDatabase
from cement import App  # type: ignore[attr-defined]
from cement.utils import fs
from seedboxsync.core.dao import Download, SeedboxSync, Torrent


def extend_db(app: App) -> None:
    """
    Extend the SeedboxSync application with a Peewee database instance.

    Args:
        app (App): The Cement App object.
    """
    db = Database(app).init()
    app.extend('_db', db)


def close_db(app: App) -> None:
    """
    Close the database connection.

    Args:
        app (App): The Cement App object.
    """
    app.log.debug('Close database')
    app._db.close()  # type: ignore[attr-defined]


def sizeof(num: float, suffix: str = 'B') -> str:
    """
    Convert a number to human-readable units (e.g., B, KiB, MiB).

    Args:
        num (float): The numeric value to convert.
        suffix (str): Suffix for the value (default: 'B').

    Returns:
        str: Human-readable string.
    """
    for unit in ("", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"):
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Yi{suffix}"


class Database:
    """
    Wrapper for SQLite database using Peewee.

    Manages database initialization, schema creation, upgrades,
    and registration of custom SQLite functions.

    Attributes:
        __DATABASE_VERSION (int): Current database version in code.
        __app (App): Cement application instance.
        db_file (str): Absolute path to the SQLite database file.
        db (SqliteDatabase): Peewee database instance.
    """

    __DATABASE_VERSION = 1
    __app: App
    __db_file: str
    db: SqliteDatabase

    def __init__(self, app: App):
        """
        Initialize the Database wrapper.

        Args:
            app (App): Cement App object.
        """
        self.__app = app
        self.__db_file = fs.abspath(self.__app.config.get('local', 'db_file'))

    def init(self) -> SqliteDatabase:
        """
        Initialize the database and return a bound Peewee instance.

        Creates the database if it does not exist, sets the schema,
        and upgrades it if necessary.

        Returns:
            SqliteDatabase: Bound Peewee database instance.
        """
        if not os.path.exists(self.__db_file):
            self.__app.log.info('DataBase "%s" does not exist, creating...' % self.__db_file)
            fs.ensure_dir_exists(os.path.dirname(self.__db_file))
            self.__init_and_bind()
            self.__set_db_schema()
        else:
            self.__init_and_bind()

        # Upgrade DB if necessary
        db_version = SeedboxSync.get_db_version()
        self.__app.log.debug('SQLite database version is %s' % db_version)
        if int(db_version) < self.__DATABASE_VERSION:
            self.__app.log.info('Upgrading database "%s" from v%s to v%s' % (self.__db_file, db_version, self.__DATABASE_VERSION))
            self.__set_db_schema()

        # Upsert SeedboxSync version
        SeedboxSync.set_version()

        return self.db

    def __init_and_bind(self) -> None:
        """
        Bind the database to Peewee models and register custom functions.
        """
        self.db = SqliteDatabase(self.__db_file)
        self.db.bind([Download, SeedboxSync, Torrent])
        self.__register_functions()

    def __set_db_schema(self) -> None:
        """
        Create tables if they do not exist and update the database version.
        """
        self.db.connect()
        self.db.create_tables([Download, Torrent, SeedboxSync], safe=True)
        SeedboxSync.set_db_version(str(self.__DATABASE_VERSION))

    def __register_functions(self) -> None:
        """
        Register custom SQLite functions for this database instance.
        """

        @self.db.func('sizeof')  # type: ignore[misc]
        def db_sizeof(num: int, suffix: str = 'B') -> str:
            """
            SQLite function to convert a number to human-readable format.

            Args:
                num (int): Numeric value.
                suffix (str): Unit suffix.

            Returns:
                str: Human-readable string.
            """
            return sizeof(num, suffix)
