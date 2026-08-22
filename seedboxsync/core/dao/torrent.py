#
# Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
"""Peewee DAO model for Torrent."""

import datetime
from peewee import AutoField, DateTimeField, TextField
from seedboxsync.core.dao import SeedboxSyncModel


class Torrent(SeedboxSyncModel):
    """
    Data Access Object (DAO) representing a torrent.

    This model stores basic metadata for a torrent, including its name,
    announce URL, and the timestamp when it was sent or added to the system.

    Attributes:
        id (int): Auto-incremented primary key.
        name (str): Name of the torrent.
        announce (str): Tracker announce URL.
        sent (datetime): Timestamp indicating when the torrent was sent or created.
    """

    id = AutoField(help_text="Unique identifier of the torrent")
    name = TextField(help_text="Name of the torrent")
    announce = TextField(null=True, help_text="Tracker announce URL of the torrent")
    sent = DateTimeField(default=datetime.datetime.now, help_text="Timestamp when the torrent was sent")
