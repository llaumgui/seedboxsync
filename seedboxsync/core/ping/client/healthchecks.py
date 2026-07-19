# -*- coding: utf-8 -*-
#
# Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
"""
Healthchecks management for SeedboxSync.
"""

import socket
import urllib.request
from seedboxsync.core import current_app
from seedboxsync.core.ping import AbstractPingClient


class Healthchecks(AbstractPingClient):
    """
    Class to manage Healthchecks's pings.
    """

    def __init__(self) -> None:
        """
        Constructor for Healthchecks.
        """
        self.app = current_app

    def start(self, sub_command: str) -> None:
        """
        Send a start ping to Healthchecks for a given subcommand.

        Args:
            sub_command (str): The SeedboxSync subcommand to ping.
        """
        enabled = self.app.seedboxsync_config.get("healthchecks_" + sub_command + "_enabled")
        if enabled is False:
            self.app.logger.warning('Healthchecks for "%s" disabled by configuration' % sub_command)
        else:
            base_url = self.app.seedboxsync_config.get("healthchecks_" + sub_command + "_ping_url", "")
            ping_url = f"{base_url.rstrip('/')}/start"
            self.app.logger.debug("Ping url: %s" % ping_url)

            try:
                urllib.request.urlopen(ping_url, timeout=10)
            except socket.error as e:
                self.app.logger.error("Healthchecks, ping failed: %s" % e)
                pass

    def success(self, sub_command: str) -> None:
        """
        Send a success ping to Healthchecks for a given subcommand.

        Args:
            sub_command (str): The SeedboxSync subcommand to ping.
        """
        enabled = self.app.seedboxsync_config.get("healthchecks_" + sub_command + "_enabled")
        if enabled is False:
            self.app.logger.warning('Healthchecks for "%s" disabled by configuration' % sub_command)
        else:
            ping_url = self.app.seedboxsync_config.get("healthchecks_" + sub_command + "_ping_url", "")
            self.app.logger.debug("Ping url: %s" % ping_url)

            try:
                urllib.request.urlopen(ping_url, timeout=10)
            except socket.error as e:
                self.app.logger.error("Healthchecks, ping failed: %s" % e)
                pass
