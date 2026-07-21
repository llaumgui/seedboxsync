#
# Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
"""Healthchecks management for SeedboxSync."""

import urllib.request
from seedboxsync.core import current_app
from seedboxsync.core.ping import AbstractPingClient


class Healthchecks(AbstractPingClient):
    """Class to manage Healthchecks's pings."""

    def __init__(self) -> None:
        """Constructor for Healthchecks."""
        self.app = current_app

    def start(self, sub_command: str) -> None:
        """
        Send a start ping to Healthchecks for a given subcommand.

        Args:
            sub_command (str): The SeedboxSync subcommand to ping.
        """
        enabled = self.app.seedboxsync_config.get("healthchecks_" + sub_command + "_enabled")
        if enabled is False:
            self.app.logger.info(f'Healthchecks for "{sub_command}" disabled by configuration')
        else:
            base_url = self.app.seedboxsync_config.get("healthchecks_" + sub_command + "_ping_url", "")
            ping_url = f"{base_url.rstrip('/')}/start"
            self.app.logger.debug(f"Ping url: {ping_url}")

            try:
                urllib.request.urlopen(ping_url, timeout=10)
            except OSError:
                self.app.logger.exception("Healthchecks, ping failed")

    def success(self, sub_command: str) -> None:
        """
        Send a success ping to Healthchecks for a given subcommand.

        Args:
            sub_command (str): The SeedboxSync subcommand to ping.
        """
        enabled = self.app.seedboxsync_config.get("healthchecks_" + sub_command + "_enabled")
        if enabled is False:
            self.app.logger.info(f'Healthchecks for "{sub_command}" disabled by configuration')
        else:
            ping_url = self.app.seedboxsync_config.get("healthchecks_" + sub_command + "_ping_url", "")
            self.app.logger.debug(f"Ping url: {ping_url}")

            try:
                urllib.request.urlopen(ping_url, timeout=10)
            except OSError:
                self.app.logger.exception("Healthchecks, ping failed.")
