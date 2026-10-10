#
# Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#

"""Database schema migration management."""

from pathlib import Path
from flask import Flask
from peewee import SqliteDatabase
from playhouse.migrations import Runner
from seedboxsync.core import utils
from seedboxsync.core.database.models import ApiKey, Download, SeedboxSync, TaskStatus, Torrent, User

database = SqliteDatabase(str(utils.get_database_path_from_paths()))
models = [ApiKey, Download, SeedboxSync, TaskStatus, Torrent, User]
MIGRATION_PATH = str(Path(__file__).parent / "migrations")


class DatabaseMigration:
    """Manage database schema migrations."""

    def __init__(self, app: Flask, db: SqliteDatabase) -> None:
        """
        Initialize the database migration manager.

        Args:
            app: Flask application instance.
            db: Peewee SQLite database instance.
        """
        self.app = app
        self.db = db
        self.runner = Runner(self.db, directory=MIGRATION_PATH)

    def upgrade(self) -> None:
        """
        Upgrade the database schema to the latest available migration.

        Existing databases using the legacy integer-based migration system
        are first converted to the Peewee migration history format.
        """
        with self.app.app_context():
            self._run_migrations()
        self._set_last_migration()

    def _run_migrations(self) -> None:
        """Apply all pending Peewee migrations."""
        applied = self.runner.up()

        for migration in applied:
            self.app.logger.info("Applied database migration: %s", migration)

    def _set_last_migration(self) -> None:
        """Store the latest available migration name in the Flask configuration."""
        migrations = self.runner.status()
        if migrations:
            self.app.config["LAST_MIGRATION"] = migrations[-1].name
