from unittest.mock import patch
from seedboxsync.core.database.migration import DatabaseMigration


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
