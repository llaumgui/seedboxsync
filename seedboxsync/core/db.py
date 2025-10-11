# -*- coding: utf-8 -*-
#
# Copyright (C) 2015-2025 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#

import os
from peewee import SqliteDatabase
from cement import App  # type: ignore[attr-defined]
from cement.utils import fs
from seedboxsync.core.dao import global_database_object, Download, SeedboxSync, Torrent


def sizeof(num: float, suffix: str = 'B') -> str:
    """
    Convert in human readable units.
    From: https://stackoverflow.com/a/1094933

    Args:
        num (int): Value not human readable.
        suffix (str): Suffix for value given to (default: B).

    Returns:
        str: Human readable value.
    """
    for unit in ("", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"):
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Yi{suffix}"


def extend_db(app: App) -> None:
    """
    Extends SeedboxSync with Peewee

    Returns:
        app (App): The Cement App object
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

    @db.func('sizeof')  # type: ignore[misc]
    def db_sizeof(num: int, suffix: str = 'B') -> str:
        return sizeof(num, suffix)

    app.extend('_db', db)


def close_db(app: App) -> None:
    """
    Close database connexion.

    Returns:
        app (App): The Cement App object
    """

    app.log.debug('Close database')
    app._db.close()  # type: ignore[attr-defined]
