#
# Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
"""Peewee DAO model for SeedboxSync."""

from peewee import CharField, TextField
from seedboxsync.core.database.models import SeedboxSyncModel


class SeedboxSync(SeedboxSyncModel):
    """
    Data Access Object (DAO) for application metadata and internal configuration.

    This table stores key-value pairs used for SeedboxSync's internal state
    management and configuration, such as taskstatus, versioning, or runtime
    parameters.

    Attributes:
        key (str): Unique identifier for the configuration entry.
        value (str): Stored value associated with the key.
    """

    key = CharField(primary_key=True, help_text="Unique identifier for the configuration entry")
    value = TextField(help_text="Value associated with the configuration entry")
