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
    A Data Access Object for Torrent.
    """
    key = CharField(unique=True)
    value = TextField()
