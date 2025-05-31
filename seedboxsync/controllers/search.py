# -*- coding: utf-8 -*-
#
# Copyright (C) 2015-2025 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#

import os
import datetime
from cement import Controller, fs, ex
from ..core.dao.torrent import Torrent
from ..core.dao.download import Download
from peewee import fn


class Search(Controller):
    """
    Controller with search concern.
    """
    class Meta:
        help = 'all search operations'
        label = 'search'
        stacked_on = 'base'
        stacked_type = 'nested'

    @ex(help='search lasts torrents uploaded from blackhole',
        arguments=[(['-n', '--number'],
                    {'help': 'number of torrents to display',
                     'action': 'store',
                     'dest': 'number',
                     'default': 10}),
                   (['-s', '--search'],
                    {'help': 'term to search',
                     'action': 'store',
                     'dest': 'term'})])
    def uploaded(self):
        """
        Search lasts torrents uploaded from blackhole
        """
        # Build "where" expression
        if self.app.pargs.term:
            where = Torrent.name.contains(self.app.pargs.term)
        else:
            where = ~(Torrent.id.contains('not_a_int'))

        # DB query
        data = Torrent.select(Torrent.id,
                              Torrent.name,
                              Torrent.sent
                              ).where(where).limit(self.app.pargs.number).order_by(Torrent.sent.desc()).dicts()
        self.app.render(reversed(data), headers={'id': 'Id', 'name': 'Name', 'sent': 'Sent datetime'})

    @ex(help='search lasts files downloaded from seedbox',
        arguments=[(['-n', '--number'],
                    {'help': 'number of torrents to display',
                     'action': 'store',
                     'dest': 'number',
                     'default': 10}),
                   (['-s', '--search'],
                    {'help': 'term to search',
                     'action': 'store',
                     'dest': 'term'})])
    def downloaded(self):
        """
        Search lasts torrents downloaded from seedbox
        """
        # Build "where" expression
        if self.app.pargs.term:
            where = (Download.finished != 0) & (Download.path.contains(self.app.pargs.term))
        else:
            where = Download.finished != 0

        # DB query
        data = Download.select(Download.id,
                               fn.SUBSTR(Download.path, -100).alias('path'),
                               Download.finished,
                               fn.sizeof(Download.local_size).alias('size')
                               ).where(where).limit(self.app.pargs.number).order_by(Download.finished.desc()).dicts()
        self.app.render(reversed(data), headers={'id': 'Id', 'finished': 'Finished', 'path': 'Path', 'size': 'Size'})

    @ex(help='search files currently in download from seedbox',
        arguments=[(['-n', '--number'],
                    {'help': 'number of torrents to display',
                     'action': 'store',
                     'dest': 'number',
                     'default': 10}),
                   (['-s', '--search'],
                    {'help': 'term to search',
                     'action': 'store',
                     'dest': 'term'})])
    def progress(self):
        """
        Search files currently in download from seedbo
        """
        # Build "where" expression
        if self.app.pargs.term:
            where = (Download.finished == 0) & (Download.path.contains(self.app.pargs.term))
        else:
            where = Download.finished == 0

        # DB suery
        data = Download.select(Download.id,
                               fn.SUBSTR(Download.path, -100).alias('path'),
                               Download.started,
                               Download.seedbox_size,
                               fn.sizeof(Download.seedbox_size).alias('size'),
                               ).where(where).limit(self.app.pargs.number).order_by(Download.started.desc()).dicts()

        in_progress = []
        part_suffix = self.app.config.get('seedbox', 'part_suffix')
        download_path = fs.abspath(self.app.config.get('local', 'download_path'))

        for torrent in data:
            full_path = fs.join(download_path, torrent.get('path') + part_suffix)
            try:
                local_size = os.stat(full_path).st_size
                progress = round(100 * (1 - ((torrent.get('seedbox_size') - local_size) / torrent.get('seedbox_size'))))
                eta = str(round(((datetime.datetime.now() - torrent.get('started')).total_seconds() / (progress / 100)) / 60)) + ' mn'
            except FileNotFoundError:
                self.app.log.warning('File not found "%s"' % full_path)
                progress = 0
                eta = "-"

            in_progress.append({
                'id': torrent.get('id'),
                'path': torrent.get('path'),
                'started': torrent.get('started'),
                'size': torrent.get('size'),
                'progress': str(progress) + '%',
                'eta': eta
            })
        self.app.render(reversed(in_progress), headers={'id': 'Id', 'started': 'Started', 'path': 'Path', 'progress': 'Progress', 'eta': 'ETA', 'size': 'Size'})
