#
# Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
"""Peewee DAO model for application log records."""

import datetime
from peewee import AutoField, CharField, DateTimeField, TextField
from seedboxsync.core.database.models import SeedboxSyncModel


class Log(SeedboxSyncModel):
    """
    Data Access Object (DAO) representing an application log record.

    Attributes:
        id: Auto-incremented primary key.
        level_name: Human-readable severity, such as ``INFO`` or ``ERROR``.
        logger_name: Name of the logger that emitted the record.
        message: Formatted log message.
        timestamp: Date and time when the record was created.
    """

    id = AutoField(help_text="Unique identifier of the log record")
    level_name = CharField(max_length=20, help_text="Severity level of the record (e.g. DEBUG, INFO, WARNING, ERROR, CRITICAL)")
    logger_name = CharField(max_length=255, help_text="Name of the logger that emitted the record")
    message = TextField(help_text="Formatted message recorded by the logger")
    timestamp = DateTimeField(default=datetime.datetime.now, help_text="Date and time when the log record was created")
