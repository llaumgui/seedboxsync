#
# Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
"""Peewee model."""

from abc import abstractmethod
import datetime
from typing import Any, cast
from peewee import Model


class SeedboxSyncModel(Model):
    """Basemodel from which all other peewee models are derived."""


class SeedboxSyncWithStatsModel(SeedboxSyncModel):
    """Basemodel from which all other peewee models are derived."""

    @classmethod
    def _get_trend(cls, current: int, previous: int) -> str:
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
            row = cls._get_period_stats(period["start"], period.get("end", None))
            previous_row = cls._get_period_stats(period["previous_start"], period["previous_end"])

            current_total = int(row["total"] or 0)
            previous_total = int(previous_row["total"] or 0)
            row["trend_total"] = cls._get_trend(current_total, previous_total)

            current_size = int(row["size"] or 0)
            previous_size = int(previous_row["size"] or 0)
            row["trend_size"] = cls._get_trend(current_size, previous_size)

            data[name] = row

        return cast(dict[str, Any], data)

    @classmethod
    @abstractmethod
    def _get_period_stats(cls, start: datetime.datetime, end: datetime.datetime | None) -> dict[str, Any]:
        """Abstract method to calculate statistics for a given period. Must be implemented by subclasses."""
