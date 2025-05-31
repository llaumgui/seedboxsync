# -*- coding: utf-8 -*-
#
# Copyright (C) 2015-2025 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#

from cement import Controller, ex
from ..core.dao.download import Download


class Clean(Controller):
    """
    Controller with clean concern.
    """
    class Meta:
        help = 'all cleaning operations'
        label = 'clean'
        stacked_on = 'base'
        stacked_type = 'nested'

    @ex(help='clean the list of files currently in download from seedbox')
    def progress(self):
        """
        List of files currently in download from seedbo
        """
        count = Download.delete().where(Download.finished == 0).execute()
        self.app.print('In progress list cleaned. %s line(s) deleted' % count)
