# -*- coding: utf-8 -*-
#
# Copyright (C) 2015-2025 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#

from importlib import import_module
from cement import App
from ..exc import SeedboxSyncError


class SyncProtocoleError(SeedboxSyncError):
    pass


class ConnectionError(SeedboxSyncError):
    pass


def extend_sync(app: App):
    """
    Extends SeedboxSync with Sync

    :param App app: the Cement App object
    """
    protocol = app.config.get('seedbox', 'protocol')
    client_class = protocol.title() + 'Client'

    app.log.debug('Extending seedboxsync application with sync (%s/%s)' % (protocol, client_class))

    try:
        client_module = import_module('..core.sync.' + protocol + '_client', 'seedboxsync.ext')
    except ImportError as exc:
        raise SyncProtocoleError('Unsupported protocole: %s: %s' % (protocol, str(exc)))

    try:
        transfer_client = getattr(client_module, client_class)
    except AttributeError:
        raise SyncProtocoleError(
            'Unsupported protocole module! No class "%s" in module "seedboxsync.core.sync.%s_client"'
            % (client_class, protocol))

    try:
        sync = transfer_client(log=app.log,
                               host=app.config.get('seedbox', 'host'),
                               port=int(app.config.get('seedbox', 'port')),
                               login=app.config.get('seedbox', 'login'),
                               password=app.config.get('seedbox', 'password'),
                               timeout=app.config.get('seedbox', 'timeout'))
    except Exception as exc:
        raise ConnectionError('Connection fail: %s' % str(exc))

    app.extend('sync', sync)


def close_sync(app: App):
    """
    Extends SeedboxSync with TinyDB

    :param App app: the Cement App object
    """
    app.log.debug('Closing sync')
    app.sync.close()
