from pathlib import Path
from unittest.mock import MagicMock, patch
from playhouse.migrations import Runner
from playhouse.schema_diff import diff_models
from seedboxsync.core.database.database import Database
from seedboxsync.core.database.migration import MIGRATION_PATH, models


def test_registered_database_functions_handle_valid_and_invalid_values(app):
    database = app.extensions["flaskdb"].database

    with app.app_context():
        row = database.execute_sql("SELECT byte_to_gi(1073741824, 'B'), humanize('invalid'), naturaldelta('invalid')").fetchone()

    assert row == ("1.0GiB", "", "a moment")


def test_new_database_is_created_with_current_model_schema(new_database_app):
    app, database_file = new_database_app
    database = app.extensions["flaskdb"].database

    assert database_file.is_file()

    schema_diff = diff_models(database, models)
    assert not schema_diff, str(schema_diff)

    migration_status = Runner(database, directory=MIGRATION_PATH).status()
    assert migration_status
    assert all(migration.path is not None for migration in migration_status)
    assert all(migration.applied is not None for migration in migration_status)


def test_database_discovers_a_writable_existing_database():
    app = MagicMock()
    app.config = {}
    database = Database.__new__(Database)
    database.app = app

    with (
        patch(
            "seedboxsync.core.database.database.utils.get_database_path_from_paths",
            return_value=Path("/data/seedboxsync.db"),
        ),
        patch.object(database, "_init_and_bind") as init_and_bind,
    ):
        database._load_database()

    assert Path(database._db_file) == Path("/data/seedboxsync.db")
    assert app.config["DATABASE"] == f"sqlite:///{Path('/data/seedboxsync.db').as_posix()}"
    init_and_bind.assert_called_once_with()


def test_database_creates_schema_when_configured_file_is_missing(tmp_path):
    database_file = tmp_path / "missing" / "seedboxsync.db"
    app = MagicMock()
    app.config = {"DATABASE": str(database_file)}
    database = Database.__new__(Database)
    database.app = app

    with (
        patch("seedboxsync.core.database.database.Path.exists", return_value=False),
        patch.object(database, "_init_and_bind") as init_and_bind,
    ):
        database._load_database()

    assert app.config["MIGRATE_DB"] is True
    init_and_bind.assert_called_once_with()


def test_database_runs_configured_migrations(tmp_path):
    app = MagicMock()
    app.config = {
        "DATABASE": f"sqlite:///{(tmp_path / 'seedboxsync.db').as_posix()}",
        "MIGRATE_DB": True,
    }
    database = Database.__new__(Database)
    database.app = app

    db_wrapper = MagicMock()
    db_wrapper.database = MagicMock()

    with (
        patch("seedboxsync.core.database.database.FlaskDB", return_value=db_wrapper),
        patch("seedboxsync.core.database.database.DatabaseMigration") as migration,
    ):
        database._init_and_bind()

    migration.assert_called_once_with(app, db_wrapper.database)
    migration.return_value.upgrade.assert_called_once_with()
