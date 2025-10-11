# -*- coding: utf-8 -*-
#
# Copyright (C) 2015-2025 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#

from peewee import CharField, TextField
from .model import SeedboxSyncModel


class SeedboxSync(SeedboxSyncModel):
    """
    Data Access Object (DAO) for application metadata and internal configuration.

    This table stores key–value pairs used for SeedboxSync's internal state
    management and configuration, such as locks, versioning, or runtime
    parameters.

    Attributes:
        key (str): Unique identifier for the configuration entry.
        value (str): Stored value associated with the key.
    """

    key = CharField(unique=True)
    value = TextField()
