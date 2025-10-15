# -*- coding: utf-8 -*-
#
# Copyright (C) 2015-2025 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
import datetime
from peewee import DateTimeField, TextField
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

    name = TextField()
    announce = TextField()
    sent = DateTimeField(default=datetime.datetime.now)
