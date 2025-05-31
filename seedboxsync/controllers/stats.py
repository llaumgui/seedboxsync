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

    @ex(help='statistics by month')
    def by_month(self):
        """
        Show statistics by month.
        """
        # DB query
        data = Download.select(Download.id,
                               Download.finished,
                               fn.strftime("%Y-%m", Download.finished).alias('month'),
                               Download.seedbox_size,
                               ).where(Download.finished != 0).order_by(Download.finished.desc()).dicts()
        tmp = {}

        for download in data:
            month = download['month']
            size = download['seedbox_size']
            if not month or not size:
                continue
            if month not in tmp:
                tmp[month] = {"files": 0, "total_size": 0.0}

            tmp[month]["files"] += 1
            tmp[month]["total_size"] += size

        stats = [
            {
                "month": month,
                "files": tmp[month]["files"],
                "total_size": sizeof(tmp[month]["total_size"]),
            }
            for month in sorted(tmp)
        ]

        self.app.render(stats, headers={'month': 'Month', 'files': 'Nb files'})
