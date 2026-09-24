#
# Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
"""Peewee DAO model for Torrent."""

from collections.abc import Iterable
import datetime
from os import PathLike
from typing import Any, cast
from urllib.parse import urlparse
from peewee import AutoField, BooleanField, DateTimeField, IntegerField, TextField, fn
import tldextract
from seedboxsync.core import utils
from seedboxsync.core.database.models import SeedboxSyncModel


class Torrent(SeedboxSyncModel):
    """
    Data Access Object (DAO) representing a torrent.

    This model stores metadata for a torrent file, including tracker info,
    source provenance, file counts, payload size, privacy status, and processing timestamp.

    Attributes:
        id (int): Auto-incremented primary key.
        name (str): Name of the torrent.
        announce (str): Tracker announce URL.
        announcer (str): Tracker announce domain name.
        source (str): Source or provenance tag of the torrent file.
        total_files (int): Total number of files contained in the torrent.
        total_size (int): Total size of all files in the torrent in bytes.
        private (bool): Flag indicating if the torrent is marked as private.
        sent (datetime): Timestamp indicating when the torrent was sent or created.
    """

    id = AutoField(help_text="Unique identifier of the torrent")
    name = TextField(help_text="Name of the torrent")
    announce = TextField(null=True, help_text="Tracker announce URL of the torrent")
    announcer = TextField(null=True, help_text="Tracker announce domain of the torrent")
    source = TextField(null=True, help_text="Source or provenance of the torrent file")
    total_files = IntegerField(null=True, help_text="Total number of files contained in the torrent")
    total_size = IntegerField(null=True, help_text="Total size of all files in bytes")
    private = BooleanField(null=False, default=False, help_text="Flag indicating if the torrent is private")
    sent = DateTimeField(default=datetime.datetime.now, help_text="Timestamp when the torrent was sent")

    def save(self, force_insert: bool = False, only: Any | None = None) -> int:
        """Save the model instance, automatically updating the announcer domain."""
        self.update_announcer()
        return super().save(force_insert=force_insert, only=only)

    def set_from_file(self, torrent_file: str | PathLike[str]) -> bool:
        """
        Populate the model from a torrent file.

        Args:
            torrent_file: Path to the torrent file.

        Returns:
            True if the torrent is valid and minimal informations was successfully extracted,
            otherwise False.
        """
        torrent_info = utils.get_torrent_infos(torrent_file)
        # Torrent is not valid
        if not isinstance(torrent_info, dict):
            return False

        # Get minimal information
        self.announce = torrent_info.get("announce") or None

        # Get extended informations
        info = torrent_info.get("info")
        if not isinstance(info, dict):
            return True

        self.source = info.get("source") or None
        self.private = info.get("private", False)

        self.total_files = None
        self.total_size = None
        files = info.get("files")
        if isinstance(files, list):
            # Multi-file torrent.
            valid_files = [file_info for file_info in files if isinstance(file_info, dict) and isinstance(file_info.get("length"), int)]
            self.total_files = len(valid_files)
            self.total_size = sum(file_info["length"] for file_info in valid_files)
        else:
            # Single-file torrent.
            length = info.get("length")
            self.total_files = 1 if isinstance(length, int) else None
            self.total_size = length if isinstance(length, int) else None

        return True

    def update_announcer(self) -> None:
        """
        Extract and populate the announcer domain from the announce URL.

        Parses ``announce`` URL and extracts the registrable domain (without subdomains).
        """
        self.announcer = None  # reset on update
        if not self.announce:
            return

        hostname = urlparse(self.announce).hostname
        if not hostname:
            return

        # Use tldextract
        extracted = tldextract.extract(hostname)
        if not extracted.domain or not extracted.suffix:
            self.announcer = hostname
            return

        self.announcer = f"{extracted.domain}.{extracted.suffix}"

    @classmethod
    def get_stats_by_announcer(cls, start_date: datetime.date | None = None, end_date: datetime.date | None = None) -> list[dict[str, Any]]:
        """
        Get the total count and total size of downloaded files grouped by MIME type.

        Args:
            start_date (datetime.date | None): Optional start date filter.
            end_date (datetime.date | None): Optional end date filter.

        Returns:
            list[dict[str, Any]]: A list of dicts containing mime_type, total count, and total_size.
        """
        # Build "where" expression
        conditions = []
        if start_date:
            conditions.append(cls.sent >= start_date)
        if end_date:
            conditions.append(cls.sent <= end_date)

        query = (
            cls.select(
                cls.announcer,
                fn.COUNT(cls.id).alias("total"),
                fn.SUM(cls.total_size).alias("total_size"),
                fn.humanize(fn.SUM(cls.total_size)).alias("human_total_size"),
            )
            .group_by(cls.announcer)
            .order_by(fn.SUM(cls.total_size).desc())
        )

        # if "where" expression
        if conditions:
            query = query.where(*conditions)
        data = query.dicts()

        return list(cast(Iterable[dict[str, Any]], data))
