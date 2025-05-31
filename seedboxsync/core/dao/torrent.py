# -*- coding: utf-8 -*-
#
# Copyright (C) 2015-2025 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#

import datetime
from peewee import AutoField, DateTimeField, TextField
from .model import SeedboxSyncModel


class Torrent(SeedboxSyncModel):
    """
    A Data Access Object for Torrent.
    """
    id = AutoField()
    name = TextField()
    announce = TextField()
    sent = DateTimeField(default=datetime.datetime.now)
