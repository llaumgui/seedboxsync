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
from seedboxsync.core.dao import Download, Lock, SeedboxSync, Torrent


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
    Close the Peewee database connection.

    Args:
        app (App): The Cement App object.
    """
    app.log.debug('Closing database connection')
    app._db.close()  # type: ignore[attr-defined]


def sizeof(num: float, suffix: str = 'B') -> str:
    """
    Convert a byte count into a human-readable string (e.g. 1.0KiB, 12.3MiB).

    Args:
        num (float): Value to convert.
        suffix (str): Unit suffix (default: 'B').

    Returns:
        str: Human-readable size string.
    """
    try:
        # Treat None or invalid type as 0
        num = float(num or 0)
    except (ValueError, TypeError):
        num = 0.0

    for unit in ("", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"):
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Yi{suffix}"


class Database:
    """
    SQLite database manager for SeedboxSync.

    Handles initialization, schema creation, migrations,
    and custom SQLite function registration.

    Attributes:
        DATABASE_VERSION (int): Target database schema version.
        __app (App): Cement application instance.
        __db_file (str): Absolute path to the SQLite database file.
        db (SqliteDatabase): Peewee database instance.
    """

    DATABASE_VERSION = 2
    __app: App
    __db_file: str
    db: SqliteDatabase

    def __init__(self, app: App):
        """
        Initialize the database manager.

        Args:
            app (App): The Cement application instance.
        """
        self.__app = app
        self.__db_file = fs.abspath(self.__app.config.get('local', 'db_file'))

    def init(self) -> SqliteDatabase:
        """
        Initialize, bind, and migrate the database as needed.

        Creates the database file if missing, binds models, and applies
        migrations sequentially until the schema matches the current
        application version.

        Returns:
            SqliteDatabase: Bound and ready-to-use database instance.
        """
        # Ensure database exists
        if not os.path.exists(self.__db_file):
            self.__app.log.info(f'Database "{self.__db_file}" not found — creating new file...')
            fs.ensure_dir_exists(os.path.dirname(self.__db_file))
            self.__init_and_bind()
            self.__create_db_schema()
        else:
            self.__init_and_bind()

        # Check and run migrations if needed
        db_version = int(SeedboxSync.get_db_version())
        self.__app.log.debug(f'SQLite database version is {db_version}')
        while db_version < self.DATABASE_VERSION:
            next_version = db_version + 1
            migration_name = f"migrate_to_{next_version}"

            self.__app.log.info(f'Upgrading database "{self.__db_file}" from v{db_version} to v{next_version}')

            # Dynamically resolve migration function
            migration_func = getattr(self, migration_name, None)
            if migration_func is None:
                raise RuntimeError(f"Missing migration function: {migration_name}")
            migration_func()
            db_version = next_version

        # Upsert SeedboxSync version
        SeedboxSync.set_version()

        return self.db

    def __init_and_bind(self) -> None:
        """
        Initialize and bind Peewee models to the SQLite database.
        """
        self.db = SqliteDatabase(self.__db_file)
        self.db.bind([Download, Lock, SeedboxSync, Torrent])
        self.__register_functions()

    def __create_db_schema(self) -> None:
        """
        Create all tables and set the initial database version.
        """
        self.db.create_tables([Download, Lock, Torrent, SeedboxSync])
        SeedboxSync.set_db_version(str(self.DATABASE_VERSION))

    def migrate_to_2(self) -> None:
        """
        Migration: rebuild SeedboxSync table and add Lock table.

        Fixes compatibility issues between tables created with Peewee v2 and v3.
        Also introduces the 'Lock' table, replacing legacy '.lock' files.
        """
        self.db.drop_tables([SeedboxSync])
        self.db.create_tables([Lock, SeedboxSync])
        SeedboxSync.set_db_version('2')

    def __register_functions(self) -> None:
        """
        Register custom SQLite functions.
        """

        @self.db.func('sizeof')  # type: ignore[misc]
        def db_sizeof(num: int, suffix: str = 'B') -> str:
            """
            SQLite function to convert a number to human-readable format.

            Args:
                num (int): Byte value.
                suffix (str): Optional unit suffix.

            Returns:
                str: Human-readable size string.
            """
            return sizeof(num, suffix)
