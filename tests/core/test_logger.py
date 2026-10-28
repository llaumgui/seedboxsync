from datetime import datetime
import logging
from unittest.mock import MagicMock
import click
from seedboxsync.core.logger import ColorFormatter, DatabaseLogHandler, configure_logger


def test_color_formatter_colors_known_levels_and_preserves_unknown_levels(monkeypatch):
    formatter = ColorFormatter("%(levelname)s %(message)s")
    warning = logging.LogRecord("test", logging.WARNING, __file__, 1, "careful", (), None)
    custom = logging.LogRecord("test", 15, __file__, 1, "plain", (), None)
    styled = MagicMock(return_value="colored warning")
    monkeypatch.setattr(click, "style", styled)

    assert formatter.format(warning) == "colored warning"
    styled.assert_called_once_with("WARNING careful", fg="yellow")
    assert formatter.format(custom) == "Level 15 plain"


def test_configure_logger_applies_formatter_to_every_handler():
    logger = logging.getLogger("seedboxsync-test-configure")
    handlers = [MagicMock(), MagicMock()]
    logger.handlers = handlers

    configure_logger(logger)

    for handler in handlers:
        formatter = handler.setFormatter.call_args.args[0]
        assert isinstance(formatter, ColorFormatter)


def test_database_log_handler_persists_log_record(new_database_app):
    from seedboxsync.core.database.models import Log

    app, _ = new_database_app
    record = logging.LogRecord("seedboxsync.test", logging.WARNING, __file__, 1, "Warning: %s", ("disk full",), None)
    record.created = datetime(2026, 1, 2, 3, 4, 5).timestamp()

    with app.app_context():
        Log.delete().execute()  # Clear existing records
        DatabaseLogHandler().emit(record)
        stored_record = Log.get()

    assert stored_record.level == "WARNING"
    assert stored_record.logger == "seedboxsync.test"
    assert stored_record.message == "Warning: disk full"
    assert stored_record.timestamp == datetime(2026, 1, 2, 3, 4, 5)


def test_database_log_handler_keeps_only_latest_max_records(new_database_app):
    from seedboxsync.core.database.models import Log

    app, _ = new_database_app
    with app.app_context():
        Log.delete().execute()  # Clear existing records
        record_to_log = DatabaseLogHandler.CLEANUP_INTERVAL + DatabaseLogHandler.MAX_RECORDS - 1
        Log.insert_many(
            [
                {
                    "level": "INFO",
                    "logger": "test",
                    "module": "icule",
                    "message": f"seed-{index}",
                    "timestamp": datetime(2026, 1, 2, 3, 4, 5),
                }
                for index in range(record_to_log)
            ]
        ).execute()

        record = logging.LogRecord("seedboxsync.test", logging.INFO, __file__, 1, "cleanup-trigger", (), None)
        DatabaseLogHandler().emit(record)

        assert Log.select().count() == DatabaseLogHandler.MAX_RECORDS
        assert Log.select().order_by(Log.id).first().message == "seed-500"
        assert Log.select().order_by(Log.id.desc()).first().message == "cleanup-trigger"


def test_configured_application_logger_persists_records(new_database_app):
    from seedboxsync.core.database.models import Log

    app, _ = new_database_app
    marker = "database-log-handler-integration-test"
    with app.app_context():
        app.logger.warning("%s", marker)
        stored_record = Log.get(Log.message == marker)

    assert stored_record.level == "WARNING"
    assert stored_record.logger == "seedboxsync"


def test_add_database_log_handler_replaces_existing_handler():
    from seedboxsync.core.logger import add_database_log_handler

    logger = logging.getLogger("seedboxsync-test-database-handler")
    logger.handlers = [MagicMock()]

    add_database_log_handler(logger)
    first_handler = next(handler for handler in logger.handlers if isinstance(handler, DatabaseLogHandler))
    add_database_log_handler(logger)

    handlers = [handler for handler in logger.handlers if isinstance(handler, DatabaseLogHandler)]
    assert len(handlers) == 1
    assert handlers[0] is not first_handler
