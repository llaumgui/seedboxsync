#
# Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
"""Flask core initer mobule."""
from functools import cached_property
from importlib import import_module
from typing import Any, cast
from flask import Flask, current_app
from seedboxsync.core import Config
from seedboxsync.core.exception import PingServiceError, SyncProtocoleError
from seedboxsync.core.ping import AbstractPingClient
from seedboxsync.core.sync import AbstractSyncClient
from seedboxsync.core.taskmanager import Manager, task_manager


class SeedboxSyncFlask(Flask):
    """Flask application with SeedboxSync-specific configuration helpers."""

    @property
    def seedboxsync_config(self) -> dict[str, Any]:
        """
        Return the SeedboxSync configuration namespace.

        Returns:
            The SeedboxSync configuration with the namespace prefix removed
            and keys converted to lowercase.
        """
        return self.config.get_namespace(Config.CONFIG_NAMESPACE)

    @cached_property
    def task_manager(self) -> Manager:
        """
        Return the task instance Manager.

        Returns:
            The task manager instance.
        """
        task_manager.init_app(self)
        return task_manager

    @cached_property
    def sync(self) -> AbstractSyncClient:
        """
        Return the configured sync client instance.

        Returns:
            AbstractSyncClient: Client instance.
        """
        protocol = self.seedboxsync_config.get("seedbox_protocol", "")
        client_class = protocol.title() + "Client"

        self.logger.debug(f"Using SeedboxSync with sync ({protocol} / {client_class})")

        # Load the client module dynamically
        try:
            client_module = import_module("seedboxsync.core.sync.client." + protocol)
        except ImportError as exc:
            raise SyncProtocoleError(f"Unsupported protocol: {protocol}: {exc!s}") from exc

        # Get the client class from the module
        try:
            transfer_client = getattr(client_module, client_class)
        except AttributeError as exc:
            raise SyncProtocoleError(
                f"Unsupported protocol module! No class \"{client_class}\" in module \"seedboxsync.core.sync.{protocol}_client\"") from exc

        # Instantiate the client
        try:
            sync_client = transfer_client()
        except Exception as exc:
            raise ConnectionError(f"{exc!s}\nFailed to establish a connection.") from exc

        return sync_client  # type: ignore[no-any-return]

    @cached_property
    def ping(self) -> AbstractPingClient:
        """
        Return the configured ping client instance.

        Returns:
            AbstractPingClient: Configured ping client instance.
        """
        ping_service = "healthchecks"
        client_class = ping_service.title()

        self.logger.debug(f"Using SeedboxSync with ping ({ping_service} / {client_class})")

        # Load the client module dynamically
        try:
            client_module = import_module("seedboxsync.core.ping.client." + ping_service)
        except ImportError as exc:
            raise PingServiceError(f"Unsupported ping service: {ping_service}: {exc!s}") from exc

        # Get the client class from the module
        try:
            ping_client = getattr(client_module, client_class)
        except AttributeError as exc:
            raise PingServiceError(
                f'Unsupported ping service module! No class "{client_class}" in module "seedboxsync.core.ping.{ping_service}client"') from exc

        return ping_client()  # type: ignore[no-any-return]


seedboxsync_current_app = cast(SeedboxSyncFlask, current_app)
