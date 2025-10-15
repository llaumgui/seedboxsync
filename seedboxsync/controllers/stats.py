# -*- coding: utf-8 -*-
#
# Copyright (C) 2015-2025 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
from cement import Controller, ex  # type: ignore[attr-defined]
from peewee import fn
from seedboxsync.core.dao import Download
from seedboxsync.core.db import sizeof


class Stats(Controller):
    """
    Controller for statistics operations in SeedboxSync.

    Provides commands to view statistics about downloaded files,
    aggregated by month, year, or as total counts and sizes.
    """

    class Meta:
        help = 'all stats operations'
        label = 'stats'
        stacked_on = 'base'
        stacked_type = 'nested'

    def __stats_by_period(self, period: str, header_label: str) -> None:
        """
        Generic helper to calculate statistics by a given period.

        Aggregates the number of files and total size for each month or year.

        Args:
            period (str): Either 'month' or 'year' to group statistics.
            header_label (str): Label used for rendering the period column.
        """
        strftime_format = "%Y-%m" if period == "month" else "%Y"

        data = Download.select(
            Download.id,
            Download.finished,
            fn.strftime(strftime_format, Download.finished).alias(period),
            Download.seedbox_size,
        ).where(Download.finished != 0).order_by(Download.finished.desc()).dicts()

        tmp = {}
        for download in data:
            key = download[period]
            size = download['seedbox_size']
            if not key or not size:
                continue
            if key not in tmp:
                tmp[key] = {"files": 0, "total_size": 0.0}
            tmp[key]["files"] += 1
            tmp[key]["total_size"] += size

        stats = [
            {
                period: key,
                "files": tmp[key]["files"],
                "total_size": sizeof(tmp[key]["total_size"]),
            }
            for key in sorted(tmp)
        ]

        self.app.render(stats, headers={period: header_label, 'files': 'Nb files', 'total_size': 'Total size'})

    @ex(help='statistics by month')
    def by_month(self) -> None:
        """
        Show statistics aggregated by month.
        """
        self.__stats_by_period('month', 'Month')

    @ex(help='statistics by year')
    def by_year(self) -> None:
        """
        Show statistics aggregated by year.
        """
        self.__stats_by_period('year', 'Year')

    @ex(help='total statistics')
    def total(self) -> None:
        """
        Show total statistics for all completed downloads.

        Displays the total number of files and the total size.
        """
        query = Download.select().where(Download.finished != 0)
        total_files = query.count()
        total_size = sum([d.seedbox_size for d in query if d.seedbox_size])

        stats = [{
            'files': total_files,
            'total_size': sizeof(total_size),
        }]

        self.app.render(stats, headers={'files': 'Nb files', 'total_size': 'Total size'})

    @ex(help='show total statistics if no subcommand is specified')
    def _default(self) -> None:
        """
        Default action when no subcommand is provided.

        Prints the parser help and shows total statistics.
        """
        self._parser.print_help()
        self.total()
