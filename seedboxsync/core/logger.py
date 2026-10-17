#
# Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
"""Setup logger for Flask."""

from datetime import datetime
import logging
from typing import ClassVar
import click
from seedboxsync.core.database.models import Log


class DatabaseLogHandler(logging.Handler):
    """Persist log records using the application's Log model."""

    CLEANUP_INTERVAL = 500
    MAX_RECORDS = 1000

    def emit(self, record: logging.LogRecord) -> None:
        """Write a formatted log record to the database."""
        try:
            log_entry = Log.create(
                level_name=record.levelname,
                logger_name=record.name,
                message=record.getMessage(),
                timestamp=datetime.fromtimestamp(record.created),
            )
            if log_entry.id % self.CLEANUP_INTERVAL == 0:
                latest_logs = Log.select(Log.id).order_by(Log.id.desc()).limit(self.MAX_RECORDS)
                Log.delete().where(Log.id.not_in(latest_logs)).execute()
        except Exception:
            self.handleError(record)


class ColorFormatter(logging.Formatter):
    """Format log records with colors based on their level."""

    COLORS: ClassVar[dict[int, str]] = {
        logging.DEBUG: "bright_black",
        logging.INFO: "blue",
        logging.WARNING: "yellow",
        logging.ERROR: "red",
        logging.CRITICAL: "bright_red",
    }

    def format(self, record: logging.LogRecord) -> str:
        """
        Format a log record and apply a color based on its log level.

        Args:
            record: The log record to format.

        Returns:
            str: The formatted and colorized log message.
        """
        message = super().format(record)
        color = self.COLORS.get(record.levelno)

        if color is None:
            return message

        return click.style(message, fg=color)


def configure_logger(logger: logging.Logger) -> None:
    """
    Configure the logger by applying the custom formatter to all existing handlers.

    Args:
        logger: The logger to configure.
    """
    formatter = ColorFormatter(
        fmt="%(asctime)s [%(levelname)-8s] [%(module)s] %(message)s",
        datefmt="%H:%M:%S",
    )

    for handler in logger.handlers:
        handler.setFormatter(formatter)


def add_database_log_handler(logger: logging.Logger) -> None:
    """
    Add a handler that persists records to the database.

    Args:
        logger: The logger to connect to the database log handler.
    """
    for handler in [handler for handler in logger.handlers if isinstance(handler, DatabaseLogHandler)]:
        logger.removeHandler(handler)
        handler.close()

    database_handler = DatabaseLogHandler()
    logger.addHandler(database_handler)
