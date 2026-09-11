#
# Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
"""Peewee DAO model for Download."""

import datetime
from peewee import AutoField, CharField, DateTimeField, IntegerField, TextField
from seedboxsync.core import utils
from seedboxsync.core.database.models import SeedboxSyncModel


class Download(SeedboxSyncModel):
    """
    Data Access Object (DAO) representing a file download.

    This model stores information about a downloaded file, including its path,
    size on the seedbox and locally, as well as timestamps indicating when
    the download started and finished.
    """

    id = AutoField(help_text="Unique identifier of the download")
    path = TextField(help_text="Path of the downloaded file")
    seedbox_size = IntegerField(help_text="Size of the file on the seedbox in bytes")
    local_size = IntegerField(default=0, help_text="Size of the downloaded file stored locally in bytes")
    mime_extension = CharField(max_length=255, default="", help_text="File extension detected during MIME analysis")
    mime_type = CharField(max_length=100, default="", help_text="MIME type detected for the file (e.g. video/mp4)")
    mime_confidence = CharField(max_length=65, default="", help_text="Confidence level or method used for MIME detection (e.g. extension, magic)")
    started = DateTimeField(default=datetime.datetime.now, help_text="Timestamp when the download started")
    finished = DateTimeField(default=0, help_text="Timestamp when the download finished")

    @classmethod
    def is_already_download(cls, filepath: str) -> bool:
        """
        Check if a file has already been downloaded.

        Args:
            filepath (str): Absolute or relative path to the file.

        Returns:
            bool: True if the file was already downloaded (i.e. has a nonzero
            ``finished`` timestamp), otherwise False.
        """
        count = cls.select().where(cls.path == filepath, cls.finished > 0).count()
        return count != 0

    def set_mime(self, save: bool = False) -> None:
        """
        Detect and update the MIME attributes of the downloaded file.

        Calls ``utils.get_mime_type_from_file`` to inspect the file path and header bytes,
        updating the ``mime_extension``, ``mime_type``, and ``mime_confidence`` attributes.

        Args:
            save (bool, optional): If True, saves the model instance to the database
                immediately after updating attributes. Defaults to False.
        """
        self.mime_type, self.mime_extension, self.mime_confidence = utils.get_mime_type_from_file(self.path)

        if save:
            self.save()
