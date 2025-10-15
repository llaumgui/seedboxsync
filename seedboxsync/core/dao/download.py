# -*- coding: utf-8 -*-
#
# Copyright (C) 2015-2025 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
import datetime
from peewee import DateTimeField, IntegerField, TextField
from seedboxsync.core.dao import SeedboxSyncModel


class Download(SeedboxSyncModel):
    """
    Data Access Object (DAO) representing a file download.

    This model stores information about a downloaded file, including its path,
    size on the seedbox and locally, as well as timestamps indicating when
    the download started and finished.
    """

    path = TextField()
    seedbox_size = IntegerField()
    local_size = IntegerField(default=0)
    started = DateTimeField(default=datetime.datetime.now)
    finished = DateTimeField(default=0)

    @staticmethod
    def is_already_download(filepath: str) -> bool:
        """
        Check if a file has already been downloaded.

        Args:
            filepath (str): Absolute or relative path to the file.

        Returns:
            bool: True if the file was already downloaded (i.e. has a nonzero
            ``finished`` timestamp), otherwise False.
        """
        count = Download.select().where(Download.path == filepath, Download.finished > 0).count()
        if count == 0:
            return False
        else:
            return True
