# -*- coding: utf-8 -*-
#
# Copyright (C) 2015-2025 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
"""
Module to extend SeedboxSync application with synchronization functionality.

Handles dynamic loading of the appropriate transport client based on configuration,
establishes connections, and provides utilities to close the client properly.
"""

from importlib import import_module
from cement import App  # type: ignore[attr-defined]
from seedboxsync.core.exc import SeedboxSyncError


class SyncProtocoleError(SeedboxSyncError):
    """
    Exception raised when an unsupported or misconfigured synchronization protocol
    is specified.
    """
    pass


class ConnectionError(SeedboxSyncError):
    """
    Exception raised when the connection to the remote seedbox fails.
    """
    pass


def extend_sync(app: App) -> None:
    """
    Extend the SeedboxSync application with a transport client.

    Dynamically loads the client class corresponding to the protocol defined
    in configuration, initializes it, and attaches it to the application.

    Args:
        app (App): The Cement App object.

    Raises:
        SyncProtocoleError: If the protocol is unsupported or the module/class cannot be loaded.
        ConnectionError: If the connection to the remote seedbox fails.
    """
    protocol = app.config.get('seedbox', 'protocol')
    client_class = protocol.title() + 'Client'

    app.log.debug('Extending SeedboxSync application with sync (%s/%s)' % (protocol, client_class))

    # Load the client module dynamically
    try:
        client_module = import_module('..core.sync.' + protocol + '_client', 'seedboxsync.ext')
    except ImportError as exc:
        raise SyncProtocoleError('Unsupported protocol: %s: %s' % (protocol, str(exc)))

    # Get the client class from the module
    try:
        transfer_client = getattr(client_module, client_class)
    except AttributeError:
        raise SyncProtocoleError(
            'Unsupported protocol module! No class "%s" in module "seedboxsync.core.sync.%s_client"'
            % (client_class, protocol))

    # Instantiate the client
    try:
        sync = transfer_client(
            log=app.log,
            host=app.config.get('seedbox', 'host'),
            port=int(app.config.get('seedbox', 'port')),
            login=app.config.get('seedbox', 'login'),
            password=app.config.get('seedbox', 'password'),
            timeout=app.config.get('seedbox', 'timeout')
        )
    except Exception as exc:
        raise ConnectionError('Connection failed: %s' % str(exc))

    # Attach the client instance to the app
    app.extend('sync', sync)


def close_sync(app: App) -> None:
    """
    Close the synchronization client and release resources.

    Args:
        app (App): The Cement App object.
    """
    app.log.debug('Closing sync')
    app.sync.close()  # type: ignore[attr-defined]
