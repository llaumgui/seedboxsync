#
# Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
"""Peewee DAO model for Download."""

from collections.abc import Iterable
import datetime
from typing import Any, cast
from peewee import AutoField, CharField, DateTimeField, IntegerField, TextField, fn
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

    @classmethod
    def get_stats_by_mime_type(cls, start_date: datetime.date | None = None, end_date: datetime.date | None = None) -> list[dict[str, Any]]:
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
            conditions.append(cls.finished >= start_date)
        if end_date:
            conditions.append(cls.finished <= end_date)

        query = (
            cls.select(
                cls.mime_type,
                fn.COUNT(cls.id).alias("total"),
                fn.SUM(cls.local_size).alias("total_size"),
                fn.humanize(fn.SUM(cls.local_size)).alias("human_total_size"),
            )
            .group_by(cls.mime_type)
            .order_by(fn.SUM(cls.local_size).desc())
        )

        # if "where" expression
        if conditions:
            query = query.where(*conditions)
        data = query.dicts()

        return list(cast(Iterable[dict[str, Any]], data))

    @classmethod
    def get_stats(cls) -> dict[str, object]:
        """
        Calculate summary download statistics across predefined time periods.

        Queries finished downloads to calculate total count, total byte size,
        human-readable file sizes, and the percentage trend compared with the
        previous equivalent period.

        Returns:
            dict[str, dict[str, Any]]: A dictionary mapping each period name
            ("day", "week", "last24h", "last7d", "last30d", "month", "year")
            to a dictionary containing:
                - total (int): Total count of finished downloads in the period.
                - size (int | None): Total size in bytes.
                - human_size (str | None): Formatted size string.
                - trend (str): Percentage change compared with the previous
                equivalent period (e.g. "+12.5%", "-8.3%", "0.0%").
        """
        now = datetime.datetime.now()
        today = now.replace(hour=0, minute=0, second=0, microsecond=0)

        periods = {
            "day": {
                "start": today,
                "previous_start": today - datetime.timedelta(days=1),
                "previous_end": today,
            },
            "week": {
                "start": today - datetime.timedelta(days=today.weekday()),
                "previous_start": today - datetime.timedelta(days=today.weekday() + 7),
                "previous_end": today - datetime.timedelta(days=today.weekday()),
            },
            "month": {
                "start": today.replace(day=1),
                "previous_start": (today.replace(day=1) - datetime.timedelta(days=1)).replace(day=1),
                "previous_end": today.replace(day=1),
            },
            "year": {
                "start": today.replace(month=1, day=1),
                "previous_start": today.replace(
                    year=today.year - 1,
                    month=1,
                    day=1,
                ),
                "previous_end": today.replace(month=1, day=1),
            },
            "last24h": {
                "start": now - datetime.timedelta(hours=24),
                "previous_start": now - datetime.timedelta(hours=48),
                "previous_end": now - datetime.timedelta(hours=24),
            },
            "last7d": {
                "start": now - datetime.timedelta(days=7),
                "previous_start": now - datetime.timedelta(days=14),
                "previous_end": now - datetime.timedelta(days=7),
            },
            "last30d": {
                "start": now - datetime.timedelta(days=30),
                "previous_start": now - datetime.timedelta(days=60),
                "previous_end": now - datetime.timedelta(days=30),
            },
        }

        data = {}

        for name, period in periods.items():
            row = cls.__get_period_stats(period["start"], period.get("end", None))
            previous_row = cls.__get_period_stats(period["previous_start"], period["previous_end"])

            current_total = int(row["total"] or 0)
            previous_total = int(previous_row["total"] or 0)
            row["trend_total"] = cls.__get_trend(current_total, previous_total)

            current_size = int(row["size"] or 0)
            previous_size = int(previous_row["size"] or 0)
            row["trend_size"] = cls.__get_trend(current_size, previous_size)

            data[name] = row

        return cast(dict[str, Any], data)

    @classmethod
    def __get_trend(cls, current: int, previous: int) -> str:
        """
        Calculate the percentage change between two values.

        Args:
            current: Current period value.
            previous: Previous equivalent period value.

        Returns:
            Percentage change formatted with an explicit sign.
        """
        if previous == 0:
            return "+∞%" if current > 0 else "0.0%"

        percentage = ((current - previous) / previous) * 100
        return f"{percentage:+.1f}%"

    @classmethod
    def __get_period_stats(cls, start: datetime.datetime, end: datetime.datetime | None = None) -> dict[str, Any]:
        """
        Calculate statistics for a given period.

        Args:
            start: Start of the period, inclusive.
            end: End of the period, exclusive.

        Returns:
            Dictionary containing total count, total size, and human-readable size.
        """
        query = cls.select(
            fn.COUNT(cls.id).alias("total"),
            fn.SUM(cls.local_size).alias("size"),
            fn.humanize(fn.SUM(cls.local_size)).alias("human_size"),
        ).where(cls.finished >= start)

        if end is not None:
            query = query.where(cls.finished < end)

        return cast(dict[str, object], query.dicts().get())
