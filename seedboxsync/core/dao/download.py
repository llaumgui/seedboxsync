# -*- coding: utf-8 -*-
#
# Copyright (C) 2015-2025 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#

import datetime
from peewee import AutoField, DateTimeField, IntegerField, TextField
from .model import SeedboxSyncModel


class Download(SeedboxSyncModel):
    """
    A Data Access Object for Torrent.
    """
    id = AutoField()
    path = TextField()
    seedbox_size = IntegerField()
    local_size = IntegerField(default=0)
    started = DateTimeField(default=datetime.datetime.now)
    finished = DateTimeField(default=0)

    def is_already_download(filepath):
        """
        Get if file was already downloaded.

        :param str filepath: the filepath
        """
        count = Download.select().where(Download.path == filepath, Download.finished > 0).count()
        if count == 0:
            return False
        else:
            return True
