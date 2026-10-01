from unittest.mock import call, patch
from peewee import SqliteDatabase
import pytest
from seedboxsync.core.database.migration import DatabaseMigration
from seedboxsync.core.database.models import SeedboxSync


def test_legacy_version_is_absent_when_metadata_table_or_value_is_missing(app):
    migration = DatabaseMigration(app, app.extensions["flaskdb"].database)

    with app.app_context():
        SeedboxSync.delete().where(SeedboxSync.key == "db_version").execute()
        assert migration._get_legacy_database_version() is None

    empty_database = SqliteDatabase(":memory:")
    try:
        migration_without_table = DatabaseMigration(app, empty_database)
        assert migration_without_table._get_legacy_database_version() is None
    finally:
        empty_database.close()

    with app.app_context(), patch.object(migration.runner, "fake") as fake:
        migration._migrate_legacy_database()
    fake.assert_not_called()

    with app.app_context():
        SeedboxSync.replace(key="db_version", value="").execute()
        assert migration._get_legacy_database_version() is None
        SeedboxSync.delete().where(SeedboxSync.key == "db_version").execute()


def test_invalid_legacy_version_raises_a_clear_error(app):
    migration = DatabaseMigration(app, app.extensions["flaskdb"].database)

    with app.app_context():
        SeedboxSync.replace(key="db_version", value="not-an-integer").execute()
        with pytest.raises(RuntimeError, match="Invalid legacy database version"):
            migration._get_legacy_database_version()
        SeedboxSync.delete().where(SeedboxSync.key == "db_version").execute()


def test_legacy_migration_marks_known_versions_and_removes_metadata(app):
    migration = DatabaseMigration(app, app.extensions["flaskdb"].database)

    with app.app_context():
        SeedboxSync.replace(key="db_version", value="4").execute()
        with patch.object(migration.runner, "fake") as fake:
            migration._migrate_legacy_database()

        assert fake.call_args_list == [call("0001_initial"), call("0002_torrent_nullable_announce"), call("0003_add_taskstatus")]
        assert SeedboxSync.get_or_none(SeedboxSync.key == "db_version") is None


def test_legacy_migration_stops_at_the_database_version(app):
    migration = DatabaseMigration(app, app.extensions["flaskdb"].database)

    with app.app_context():
        SeedboxSync.replace(key="db_version", value="1").execute()
        with patch.object(migration.runner, "fake") as fake:
            migration._migrate_legacy_database()

        fake.assert_called_once_with("0001_initial")
        assert SeedboxSync.get_or_none(SeedboxSync.key == "db_version") is None


def test_migration_helpers_log_applied_migrations_and_store_latest_name(app):
    migration = DatabaseMigration(app, app.extensions["flaskdb"].database)
    with patch.object(migration.runner, "up", return_value=["0004_latest"]) as run:
        migration._run_migrations()
    run.assert_called_once_with()

    with patch.object(migration.runner, "status", return_value=[type("Migration", (), {"name": "0004_latest"})()]):
        migration._set_last_migration()
    assert app.config["LAST_MIGRATION"] == "0004_latest"

    app.config.pop("LAST_MIGRATION")
    with patch.object(migration.runner, "status", return_value=[]):
        migration._set_last_migration()
    assert "LAST_MIGRATION" not in app.config


def test_upgrade_runs_legacy_conversion_migrations_and_status_update(app):
    migration = DatabaseMigration(app, app.extensions["flaskdb"].database)
    with (
        patch.object(migration, "_migrate_legacy_database") as convert,
        patch.object(migration, "_run_migrations") as run,
        patch.object(migration, "_set_last_migration") as set_status,
    ):
        migration.upgrade()

    convert.assert_called_once_with()
    run.assert_called_once_with()
    set_status.assert_called_once_with()
