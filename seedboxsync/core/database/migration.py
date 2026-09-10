#
# Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#

"""Database schema migration management."""

from flask import Flask
from peewee import SqliteDatabase
from playhouse.migrations import Runner
from seedboxsync.core import utils
from seedboxsync.core.database.dao import ApiKey, Download, SeedboxSync, TaskStatus, Torrent, User

database = SqliteDatabase(str(utils.get_database_path_from_paths()))
models = [ApiKey, Download, SeedboxSync, TaskStatus, Torrent, User]
MIGRATION_PATH = "seedboxsync/core/database/migrations/"

# Map each legacy database version to the latest equivalent migration
# managed by the Peewee migration runner.
LEGACY_MIGRATION_MAP: dict[int, str | None] = {
    1: "0001_initial",
    2: None,
    3: "0002_torrent_nullable_announce",
    4: "0003_add_taskstatus",
}


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
        self._migrate_legacy_database()
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

    def _migrate_legacy_database(self) -> None:
        """
        Convert a database using the legacy migration system.

        Legacy SeedboxSync releases stored an integer database version in the
        ``seedboxsync`` table. The corresponding Peewee migrations are marked
        as already applied without executing them again.

        Databases that do not contain a legacy version are left untouched.
        """
        db_version = self._get_legacy_database_version()

        if db_version is None:
            return

        self.app.logger.info("Legacy database detected at version %d; converting migration history to Peewee migrations.", db_version)
        for version, migration_name in LEGACY_MIGRATION_MAP.items():
            if version > db_version:
                break
            if migration_name is None:
                continue
            self.app.logger.info("Marking legacy database version %d as migration '%s' already applied.", version, migration_name)
            self.runner.fake(migration_name)

        self._remove_legacy_database_version()

    def _get_legacy_database_version(self) -> int | None:
        """
        Return the legacy database version if one exists.

        Returns:
            The legacy database version, or ``None`` when the database does
            not use the legacy migration system.
        """
        if "seedboxsync" not in self.db.get_tables():
            return None

        version = SeedboxSync.select(SeedboxSync.value).where(SeedboxSync.key == "db_version").first()

        if version is None or not version.value:
            return None

        try:
            return int(version.value)
        except (TypeError, ValueError) as exc:
            raise RuntimeError(f"Invalid legacy database version: {version.value!r}") from exc

    def _remove_legacy_database_version(self) -> None:
        """Remove the obsolete legacy database version entry."""
        (SeedboxSync.delete().where(SeedboxSync.key == "db_version").execute())
        self.app.logger.debug("Removed legacy database version metadata.")
