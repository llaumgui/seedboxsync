# -*- coding: utf-8 -*-
#
# Copyright (C) 2015-2025 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#

from cement import Controller, ex
from ..core.dao.download import Download
from peewee import fn
from ..core.db import sizeof


class Stats(Controller):
    """
    Controller with statistics concern.
    """
    class Meta:
        help = 'all stats operations'
        label = 'stats'
        stacked_on = 'base'
        stacked_type = 'nested'

    def __stats_by_period(self, period, header_label):
        """
        Generic stats by period (month or year).
        :param period: 'month' or 'year'
        :param header_label: Header label for rendering
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
    def by_month(self):
        """
        Show statistics by month.
        """
        self.__stats_by_period('month', 'Month')

    @ex(help='statistics by year')
    def by_year(self):
        """
        Show statistics by year.
        """
        self.__stats_by_period('year', 'Year')
