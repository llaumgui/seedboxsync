#
# Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
"""Database module."""

from os import fspath
from pathlib import Path
from typing import ClassVar, cast
from flask import Flask
from humanize import filesize, time
from peewee import SqliteDatabase
from playhouse.flask_utils import FlaskDB
from seedboxsync.core import utils
from seedboxsync.core.database.migration import DatabaseMigration
from seedboxsync.core.database.models import ApiKey, Download, SeedboxSync, TaskStatus, Torrent, User


class Database:
    """
    Database manager for SeedboxSync using Peewee ORM.

    Handles database path resolution, connection binding, SQLite optimization
    pragmas, schema migrations, and custom SQLite functions.

    Attributes:
        DB_PATHS (ClassVar[list[Path]]): Candidate database paths checked in order of preference.
        app (Flask): The Flask application instance bound to this database.
        db (SqliteDatabase): The initialized Peewee SQLite database instance.
    """

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
        """
        Locate, configure, and initialize the SQLite database.

        Checks candidate file paths or pre-configured settings, creates parent
        directories if necessary, builds the schema for new files, and executes
        pending migrations.

        Raises:
            RuntimeError: If a required migration method is missing.
        """
        if self.app.config.get("DATABASE", False):
            # Load from testing
            self._db_file = self.app.config.get("DATABASE", "")
            self.app.config["DATABASE"] = f"sqlite:///{Path(self._db_file).as_posix()}"
        else:
            # Get DB from path
            db_path = utils.get_database_path_from_paths()
            self.app.config["DATABASE"] = fspath(db_path)
            self.app.logger.debug("Use database path %s", db_path)
            self._db_file = self.app.config["DATABASE"]
            self.app.config["DATABASE"] = f"sqlite:///{Path(self._db_file).as_posix()}"

        if not Path(self._db_file).exists():
            self.app.logger.warning(f'Database "{self._db_file}" not found — creating new file...')
            self.app.config["MIGRATE_DB"] = True

        self._init_and_bind()

    def _init_and_bind(self) -> None:
        """
        Initialize the Flask-Peewee wrapper and apply performance tuning pragmas.

        Binds model classes to the database connection and configures WAL mode,
        cache size, and foreign key constraints.
        """
        db_wrapper = FlaskDB(self.app)
        self.db = cast(SqliteDatabase, db_wrapper.database)
        self.app.extensions["flaskdb"] = db_wrapper
        self.db.journal_mode = "wal"
        self.db.cache_size = -64000
        self.db.foreign_keys = 1
        self.db.bind([ApiKey, Download, SeedboxSync, TaskStatus, Torrent, User])
        self.app.logger.debug(
            "Database initialized %s / journal_mode=%s, cache_size=%s, foreign_keys=%s",
            self.app.config["DATABASE"],
            self.db.journal_mode,
            self.db.cache_size,
            self.db.foreign_keys,
        )
        if self.app.config.get("MIGRATE_DB", False):
            DatabaseMigration(self.app, self.db).upgrade()

    def _register_functions(self) -> None:
        """Register custom SQLite scalar functions for SQL queries."""

        @self.db.func("byte_to_gi")
        def db_byte_to_gi(num: float, suffix: str = "B") -> str:  # pyright: ignore [reportUnusedFunction]
            """Convert byte counts to human-readable binary unit strings."""
            return utils.byte_to_gi(num, suffix)

        @self.db.func("humanize")
        def db_humanize(num: float) -> str:  # pyright: ignore [reportUnusedFunction]
            """Format file size numbers into human-readable representations."""
            try:
                # Treat None or invalid type as 0
                num = float(num or 0)
            except (ValueError, TypeError):
                num = 0.0
            return filesize.naturalsize(num, True)

        @self.db.func("naturaldelta")
        def db_naturaldelta(num: float) -> str:  # pyright: ignore [reportUnusedFunction]
            """Format second intervals into human-readable duration strings."""
            try:
                # Treat None or invalid type as 0
                num = float(num or 0)
            except (ValueError, TypeError):
                num = 0.0
            return time.naturaldelta(num, minimum_unit="seconds", months=False)
