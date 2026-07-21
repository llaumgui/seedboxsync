#
# Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
"""
Abstract transport client using paramiko-like interface.

This class defines the interface that all transport clients must implement,
providing methods for file operations and session management on a remote server.
"""

from abc import ABCMeta, abstractmethod


class AbstractPingClient:  # pragma: no cover
    """
    Abstract base class for transport clients.

    All concrete clients must implement methods to manage file transfers
    and remote file operations.
    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self) -> None:
        """Init method."""

    @abstractmethod
    def start(self, sub_command: str) -> None:
        """
        Send a start ping  for a given subcommand.

        Args:
            sub_command (str): The SeedboxSync subcommand to ping.
        """

    @abstractmethod
    def success(self, sub_command: str) -> None:
        """
        Send a success ping for a given subcommand.

        Args:
            sub_command (str): The SeedboxSync subcommand to ping.
        """
