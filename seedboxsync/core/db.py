#
# Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
"""Database module."""

import os
from os import fspath
from pathlib import Path
from typing import ClassVar, cast
from flask import Flask
from humanize import filesize, time
from peewee import SqliteDatabase
from playhouse.flask_utils import FlaskDB
from playhouse.migrate import SchemaMigrator, migrate
from seedboxsync.core import utils
from seedboxsync.core.dao import Download, SeedboxSync, TaskStatus, Torrent, User


class Database:
    """
    Database connector using peewee.

    Attributes:
        app (Flask): The Flask application that owns the database connection.
    """

    DATABASE_VERSION = 5
    DB_PATHS: ClassVar[list[Path]] = [
        Path("~/.config/seedboxsync/seedboxsync.db").expanduser().resolve(),
        Path("~/.seedboxsync.db").expanduser().resolve(),
        Path("~/.seedboxsync/config/seedboxsync.db").expanduser().resolve(),
        Path("/etc/seedboxsync/seedboxsync.db"),
    ]
    db: SqliteDatabase

    def __init__(self, app: Flask) -> None:
        """
        Initialize a new Database instance.

        Args:
            app (Flask): The Flask application to bind to the database.
        """
        self.app = app
        self._load_database()
        self._register_functions()

    def _load_database(self) -> None:
        """Load SeedboxSync DB from SeedboxSyncFront."""
        if self.app.config.get("DATABASE", False):
            # Load from testing
            self._db_file = self.app.config.get("DATABASE", "")
            self.app.config["DATABASE"] = "sqlite:///" + self._db_file
        else:
            # Get DB from paths, default to first path if none found
            self.app.config.setdefault("DATABASE", fspath(Database.DB_PATHS[0]))  # default path
            for path in Database.DB_PATHS:
                if path.exists() and path.is_file() and os.access(path, os.W_OK):
                    self.app.config.setdefault("DATABASE", fspath(path))
                    self.app.logger.debug("Use database path %s", path)
            self._db_file = self.app.config["DATABASE"]
            self.app.config["DATABASE"] = "sqlite:///" + self._db_file

        if not Path(self._db_file).exists():
            self.app.logger.warning(f'Database "{self._db_file}" not found — creating new file...')
            utils.ensure_dir_exists(Path(self._db_file).parent)
            self._init_and_bind()
            self._create_db_schema()
        else:
            self._init_and_bind()

        # Check and run migrations if needed
        db_version = int(SeedboxSync.get_db_version())
        self.app.logger.debug(f"SQLite database version is {db_version}")
        while db_version < self.DATABASE_VERSION:
            next_version = db_version + 1
            migration_name = f"migrate_to_{next_version}"

            self.app.logger.info(f'Upgrading database "{self._db_file}" from v{db_version} to v{next_version}')

            # Dynamically resolve migration function
            migration_func = getattr(self, migration_name, None)
            if migration_func is None:
                raise RuntimeError(f"Missing migration function: {migration_name}")
            migration_func()
            db_version = next_version

    def _init_and_bind(self) -> None:
        """Initialize and bind Peewee models to the SQLite database."""
        db_wrapper = FlaskDB(self.app)
        self.db = cast(SqliteDatabase, db_wrapper.database)
        self.app.extensions["flaskdb"] = db_wrapper
        self.db.journal_mode = "wal"
        self.db.cache_size = -64000
        self.db.foreign_keys = 1
        self.db.bind([Download, SeedboxSync, TaskStatus, Torrent, User])
        self.app.logger.debug(
            "Database initialized %s / journal_mode=%s, cache_size=%s, foreign_keys=%s",
            self.app.config["DATABASE"],
            self.db.journal_mode,
            self.db.cache_size,
            self.db.foreign_keys,
        )

    def _register_functions(self) -> None:
        """Register DB functions."""

        @self.db.func("byte_to_gi")
        def db_byte_to_gi(num: float, suffix: str = "B") -> str:  # pyright: ignore [reportUnusedFunction]
            return utils.byte_to_gi(num, suffix)

        @self.db.func("humanize")
        def db_humanize(num: float) -> str:  # pyright: ignore [reportUnusedFunction]
            try:
                # Treat None or invalid type as 0
                num = float(num or 0)
            except (ValueError, TypeError):
                num = 0.0
            return filesize.naturalsize(num, True)

        @self.db.func("naturaldelta")
        def db_naturaldelta(num: float) -> str:  # pyright: ignore [reportUnusedFunction]
            try:
                # Treat None or invalid type as 0
                num = float(num or 0)
            except (ValueError, TypeError):
                num = 0.0
            return time.naturaldelta(num, minimum_unit="seconds", months=False)

    #
    # Database creation and migration
    #
    def _create_db_schema(self) -> None:
        """Create all tables and set the initial database version."""
        self.db.create_tables([Download, SeedboxSync, TaskStatus, Torrent, User])
        SeedboxSync.set_db_version(str(self.DATABASE_VERSION))

    def migrate_to_2(self) -> None:
        """
        Migration: rebuild SeedboxSync table and add Lock table.

        Fixes compatibility issues between tables created with Peewee v2 and v3.
        """
        self.db.drop_tables([SeedboxSync])
        self.db.create_tables([SeedboxSync])
        SeedboxSync.set_db_version("2")

    def migrate_to_3(self) -> None:
        """Migration: allow null values for the 'announce' field in the torrent table."""
        migrator = SchemaMigrator.from_database(self.db)
        migrate(
            migrator.drop_not_null("torrent", "announce"),
        )
        SeedboxSync.set_db_version("3")

    def migrate_to_4(self) -> None:
        """Replace 'Lock' table by 'TaskStatus'."""
        self.db.execute_sql("DROP TABLE IF EXISTS lock;")  # type: ignore[no-untyped-call]
        self.db.execute_sql("DELETE FROM seedboxsync WHERE key = 'version';")  # type: ignore[no-untyped-call]
        self.db.create_tables([TaskStatus])

        SeedboxSync.set_db_version("4")

    def migrate_to_5(self) -> None:
        """Add user table."""
        self.db.create_tables([User])
        User.create(
            username="admin",
            password="scrypt:32768:8:1$2xZqYGaVsWgvXn8Q$b0ef299478983c1ce62090ae4a7830a09fedff434835cb983ad96a2"
            "e3719d180bf2256fe0109cf89a6d01f5ffe0159450d527ad331bb5e29e9392565c6782417",  # sonar:python:S2068=false
            email="admin@admin.ltd",
        )

        SeedboxSync.set_db_version("5")
