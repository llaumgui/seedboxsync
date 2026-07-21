from unittest.mock import MagicMock, patch
import pytest
from seedboxsync.core.dao import Download, SeedboxSync, TaskStatus, Torrent
from seedboxsync.core.db import Database


def test_registered_database_functions_handle_valid_and_invalid_values(app):
    database = app.extensions["flaskdb"].database

    with app.app_context():
        row = database.execute_sql(
            "SELECT byte_to_gi(1073741824, 'B'), humanize('invalid'), naturaldelta('invalid')"
        ).fetchone()

    assert row == ("1.0GiB", "0 Bytes", "a moment")


def test_database_discovers_a_writable_existing_database():
    app = MagicMock()
    app.config = {}
    database = Database.__new__(Database)
    database.app = app

    with (
        patch.object(Database, "DB_PATHS", ["/data/seedboxsync.db"]),
        patch("seedboxsync.core.db.Path.exists", return_value=True),
        patch("seedboxsync.core.db.Path.is_file", return_value=True),
        patch("seedboxsync.core.db.os.access", return_value=True),
        patch.object(database, "_init_and_bind") as init_and_bind,
        patch("seedboxsync.core.db.SeedboxSync.get_db_version", return_value="4"),
    ):
        database._load_database()

    assert database._db_file == "/data/seedboxsync.db"
    assert app.config["DATABASE"] == "sqlite:////data/seedboxsync.db"
    init_and_bind.assert_called_once_with()


def test_database_creates_schema_when_configured_file_is_missing(tmp_path):
    database_file = tmp_path / "missing" / "seedboxsync.db"
    app = MagicMock()
    app.config = {"DATABASE": str(database_file)}
    database = Database.__new__(Database)
    database.app = app

    with (
        patch("seedboxsync.core.db.Path.exists", return_value=False),
        patch("seedboxsync.core.db.fs.ensure_dir_exists") as ensure_directory,
        patch.object(database, "_init_and_bind") as init_and_bind,
        patch.object(database, "_create_db_schema") as create_schema,
        patch("seedboxsync.core.db.SeedboxSync.get_db_version", return_value="4"),
    ):
        database._load_database()

    ensure_directory.assert_called_once_with(str(database_file.parent))
    init_and_bind.assert_called_once_with()
    create_schema.assert_called_once_with()


def test_database_reports_a_missing_migration(tmp_path):
    database_file = tmp_path / "seedboxsync.db"
    app = MagicMock()
    app.config = {"DATABASE": str(database_file)}
    database = Database.__new__(Database)
    database.app = app
    database.DATABASE_VERSION = 1

    with (
        patch("seedboxsync.core.db.Path.exists", return_value=True),
        patch.object(database, "_init_and_bind"),
        patch("seedboxsync.core.db.SeedboxSync.get_db_version", return_value="0"),
        pytest.raises(RuntimeError, match="Missing migration function: migrate_to_1"),
    ):
        database._load_database()


def test_schema_creation_and_v2_migration_update_expected_tables():
    database = Database.__new__(Database)
    database.db = MagicMock()

    with patch("seedboxsync.core.db.SeedboxSync.set_db_version") as set_version:
        database._create_db_schema()
        database.migrate_to_2()

    assert database.db.create_tables.call_args_list[0].args == ([Download, Torrent, TaskStatus, SeedboxSync],)
    assert database.db.drop_tables.call_args.args == ([SeedboxSync],)
    assert database.db.create_tables.call_args_list[1].args == ([SeedboxSync],)
    assert [item.args[0] for item in set_version.call_args_list] == ["4", "2"]
