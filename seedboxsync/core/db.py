# -*- coding: utf-8 -*-
#
# Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
import os
import humanize
from flask import Flask
from playhouse.flask_utils import FlaskDB
from playhouse.migrate import SchemaMigrator, migrate
from seedboxsync.core.dao import Download, SeedboxSync, TaskStatus, Torrent
from seedboxsync.core.utils import byte_to_gi
from seedboxsync.core import fs


class Database(object):
    """
    Database connector using peewee.

    Attributes:
        app (Flask): The Flask application that owns the database connection.
    """

    DATABASE_VERSION = 4
    DB_PATHS = [
        os.path.expanduser("~/.config/seedboxsync/seedboxsync.db"),
        os.path.expanduser("~/.seedboxsync.db"),
        os.path.expanduser("~/.seedboxsync/config/seedboxsync.db"),
        "/etc/seedboxsync/seedboxsync.db",
    ]

    def __init__(self, app: Flask):
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
            self._db_file = self.app.config.get("DATABASE") or ""
            self.app.config["DATABASE"] = "sqlite:///" + self._db_file
        else:
            # Get DB from paths, default to first path if none found
            self.app.config.setdefault("DATABASE", Database.DB_PATHS[0])  # default path
            for path in Database.DB_PATHS:
                if os.path.exists(path) and os.path.isfile(path) and os.access(path, os.W_OK):
                    self.app.config.setdefault("DATABASE", path)
                    self.app.logger.debug("Use database path %s", path)
            self._db_file = self.app.config["DATABASE"]
            self.app.config["DATABASE"] = "sqlite:///" + self._db_file

        if not os.path.exists(self._db_file):
            self.app.logger.warning(f'Database "{self._db_file}" not found — creating new file...')
            fs.ensure_dir_exists(os.path.dirname(self._db_file))
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
        self.db = db_wrapper.database
        self.app.extensions["flaskdb"] = db_wrapper
        self.db.journal_mode = "wal"
        self.db.cache_size = -64000
        self.db.foreign_keys = 1
        self.db.bind([Download, SeedboxSync, TaskStatus, Torrent])
        self.app.logger.debug(
            "Database initialized %s / journal_mode=%s, cache_size=%s, foreign_keys=%s",
            self.app.config["DATABASE"],
            self.db.journal_mode,
            self.db.cache_size,
            self.db.foreign_keys,
        )

    def _register_functions(self) -> None:
        """Register DB functions."""

        @self.db.func("byte_to_gi")  # type: ignore
        def db_byte_to_gi(num: float, suffix: str = "B") -> str:
            return byte_to_gi(num, suffix)

        @self.db.func("humanize")  # type: ignore
        def db_humanize(num: float) -> str:
            try:
                # Treat None or invalid type as 0
                num = float(num or 0)
            except (ValueError, TypeError):
                num = 0.0
            return humanize.filesize.naturalsize(num, True)

        @self.db.func("naturaldelta")  # type: ignore
        def db_naturaldelta(num: float) -> str:
            try:
                # Treat None or invalid type as 0
                num = float(num or 0)
            except (ValueError, TypeError):
                num = 0.0
            return humanize.time.naturaldelta(num, minimum_unit="seconds", months=False)

    #
    # Database creation and migration
    #
    def _create_db_schema(self) -> None:
        """Create all tables and set the initial database version."""
        self.db.create_tables([Download, Torrent, TaskStatus, SeedboxSync])
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
        """
        Migration: allow null values for the 'announce' field in the torrent table.
        """
        migrator = SchemaMigrator.from_database(self.db)
        migrate(
            migrator.drop_not_null("torrent", "announce"),
        )
        SeedboxSync.set_db_version("3")

    def migrate_to_4(self) -> None:
        """
        Replace 'Lock' table by 'TaskStatus'.
        """
        self.db.execute_sql("DROP TABLE IF EXISTS lock;")
        self.db.execute_sql("DELETE FROM seedboxsync WHERE key = 'version';")
        self.db.create_tables([TaskStatus])

        SeedboxSync.set_db_version("4")
