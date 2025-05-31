# -*- coding: utf-8 -*-
#
# Copyright (C) 2015-2025 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#

import os
from peewee import SqliteDatabase
from cement import App
from cement.utils import fs
from .dao.model import global_database_object
from .dao.seedboxsync import SeedboxSync
from .dao.download import Download
from .dao.torrent import Torrent


def extend_db(app: App):
    """
    Extends SeedboxSync with Peewee

    :param App app: the Cement App object
    """
    db_file = fs.abspath(app.config.get('local', 'db_file'))

    app.log.debug('Extending seedboxsync application with Peewee (%s)' % db_file)

    if not os.path.exists(db_file):
        app.log.info('DataBase "%s" not exists, need to be create' % db_file)
        fs.ensure_dir_exists(os.path.dirname(db_file))
        db = SqliteDatabase(db_file)
        global_database_object.initialize(db)
        db.connect()
        db.create_tables([Download, Torrent, SeedboxSync])
        db_version = SeedboxSync.create(key='db_version', value='1')
        db_version.save()
    else:
        db = SqliteDatabase(db_file)
        global_database_object.initialize(db)

    @db.func('sizeof')
    def sizeof(num, suffix='B'):
        """
        Convert in human readable units.

        From: https://stackoverflow.com/a/1094933
        """
        for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
            if abs(num) < 1024.0:
                return "%3.1f%s%s" % (num, unit, suffix)
            num /= 1024.0
        return "%.1f%s%s" % (num, 'Yi', suffix)

    app.extend('_db', db)


def close_db(app: App):
    """
    Close database
    """

    app.log.debug('Close database')
    app._db.close()
