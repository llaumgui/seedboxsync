# -*- coding: utf-8 -*-
#
# Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
"""
Build a context used by Click.
"""

import click
from collections.abc import Iterable
from functools import cached_property
from typing import Any
from importlib import import_module
from tabulate import tabulate
from seedboxsync.cli.exception import SyncProtocoleError
from seedboxsync.core import Flask, current_app
from seedboxsync.core.lock import Lock
from seedboxsync.core.sync import AbstractSyncClient
from seedboxsync.core.ping import AbstractPingClient
from seedboxsync.core.ping.client.healthchecks import Healthchecks


class Context(click.Context):
    """
    SeedboxSync Click context.

    Args:
        ctx (click.Context): The Click context object.
    """

    @cached_property
    def app(self) -> Flask:
        """
        Return the current Flask application.

        Returns:
            Flask: The current Flask application.
        """
        return current_app

    @cached_property
    def lock(self) -> Lock:
        """
        Return a Lock instance.

        Returns:
            Lock: Lock instance.
        """
        return Lock()

    @cached_property
    def sync(self) -> AbstractSyncClient:
        """
        Return the configured sync client instance.


        Returns:
            AbstractSyncClient: Client instance.
        """
        return self._init_sync_client()

    @cached_property
    def ping(self) -> AbstractPingClient:
        """
        Return the configured sync client instance.


        Returns:
            AbstractPingClient: Client instance.
        """
        return self._init_ping_client()

    def render(self, data: Iterable[Any], headers: Iterable[Any], tablefmt: str = "github") -> Any:
        """
        Render tabular data using the specified output format.

        Args:
            data: Tabular data to render.
            headers: Column headers passed to ``tabulate``.
            tablefmt: Output table format.

        Returns:
            str: The formatted table.
        """
        return tabulate(data, headers=headers, tablefmt=tablefmt)

    def _init_sync_client(self) -> AbstractSyncClient:
        """
        Return the configured sync client instance.


        Returns:
            AbstractSyncClient: Client instance.
        """
        protocol = self.app.seedboxsync_config.get("seedbox_protocol") or ""
        client_class = protocol.title() + "Client"

        self.app.logger.debug("Using SeedboxSync with sync (%s / %s)" % (protocol, client_class))

        # Load the client module dynamically
        try:
            client_module = import_module("seedboxsync.core.sync.client." + protocol)
        except ImportError as exc:
            raise SyncProtocoleError("Unsupported protocol: %s: %s" % (protocol, str(exc)))

        # Get the client class from the module
        try:
            transfer_client = getattr(client_module, client_class)
        except AttributeError:
            raise SyncProtocoleError('Unsupported protocol module! No class "%s" in module "seedboxsync.core.sync.%s_client"' % (client_class, protocol))

        # Instantiate the client
        try:
            sync = transfer_client()
        except Exception as exc:
            raise ConnectionError(f"{str(exc)}\nFailed to establish a connection.")

        return sync  # type: ignore[no-any-return]

    def _init_ping_client(self) -> AbstractPingClient:
        """
        Return the configured ping client instance.


        Returns:
            AbstractSyncClient: Client instance.
        """
        return Healthchecks()
