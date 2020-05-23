# -*- coding: utf-8 -*-
#
# Copyright (C) 2015-2020 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#

from cement import Controller, ex
from ..core.dao.torrent import Torrent
from ..core.dao.download import Download
from peewee import fn


class List(Controller):
    """
    Controller with list concern.
    """
    class Meta:
        label = 'list'
        stacked_type = 'embedded'
        stacked_on = 'base'

    @ex(help='list of lasts torrents uploaded from blackhole',
        arguments=[(['-n', '--number'],
                    {'help': 'number of torrents to display',
                     'action': 'store',
                     'dest': 'number',
                     'default': 10})])
    def list_uploaded(self):
        """
        List of lasts torrents uploaded from blackhole
        """
        data = Torrent.select(Torrent.id, Torrent.name, Torrent.sent).limit(self.app.pargs.number).order_by(Torrent.sent.desc()).dicts()
        self.app.render(reversed(data), headers={'id': 'Id', 'name': 'Name', 'sent': 'Sent datetime'})

    @ex(help='list of lasts files downloaded from seedbox',
        arguments=[(['-n', '--number'],
                    {'help': 'number of torrents to display',
                     'action': 'store',
                     'dest': 'number',
                     'default': 10})])
    def list_downloaded(self):
        """
        List of lasts torrents downloaded from seedbox
        """
        data = Download.select(Download.id,
                               fn.SUBSTR(Download.path, -100).alias('path'),
                               Download.finished,
                               fn.sizeof(Download.local_size).alias('size')
                               ).where(Download.finished != 0).limit(self.app.pargs.number).order_by(Download.finished.desc()).dicts()
        self.app.render(reversed(data), headers={'id': 'Id', 'finished': 'Finished', 'path': 'Path', 'size': 'Size'})

    @ex(help='list of files currently in download from seedbox',
        arguments=[(['-n', '--number'],
                    {'help': 'number of torrents to display',
                     'action': 'store',
                     'dest': 'number',
                     'default': 10})])
    def list_in_progress(self):
        """
        List of files currently in download from seedbo
        """
        data = Download.select(Download.id,
                               fn.SUBSTR(Download.path, -100).alias('path'),
                               Download.started,
                               fn.sizeof(Download.seedbox_size).alias('size')
                               ).where(Download.finished == 0).limit(self.app.pargs.number).order_by(Download.started.desc()).dicts()
        self.app.render(reversed(data), headers={'id': 'Id', 'started': 'Started', 'path': 'Path', 'size': 'Size'})
