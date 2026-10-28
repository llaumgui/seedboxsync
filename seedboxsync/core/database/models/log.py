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
        level: Human-readable severity, such as ``INFO`` or ``ERROR``.
        logger: Name of the logger that emitted the record.
        module: Module of the logger that emitted the record.
        message: Formatted log message.
        timestamp: Date and time when the record was created.
    """

    id = AutoField(help_text="Unique identifier of the log record")
    level = CharField(max_length=20, default="", help_text="Severity level of the record (e.g. DEBUG, INFO, WARNING, ERROR, CRITICAL)")
    logger = CharField(max_length=255, default="", help_text="Name of the logger that emitted the record")
    module = CharField(max_length=255, default="", help_text="Module of the logger that emitted the record")
    message = TextField(default="", help_text="Formatted message recorded by the logger")
    timestamp = DateTimeField(default=datetime.datetime.now, help_text="Date and time when the log record was created")
