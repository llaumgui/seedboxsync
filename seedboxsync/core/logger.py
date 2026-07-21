#
# Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
"""Setup logger for Flask."""

import logging
from typing import ClassVar
import click


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
