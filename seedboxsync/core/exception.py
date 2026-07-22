#
# Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
"""
Custom exception classes for SeedboxSync.

This module defines the base error hierarchy used throughout the SeedboxSync
application. All exceptions inherit from `SeedboxSyncError`, which handles
logging and process termination in case of fatal errors.
"""

import logging
import sys

logger = logging.getLogger(__name__)


class SeedboxSyncError(Exception):
    """
    Base exception class for all SeedboxSync errors.

    When raised, this exception logs the error message and terminates
    the program immediately. It is intended for unrecoverable errors
    that prevent normal operation.

    Args:
        msg (str): The error message to log and display before exiting.
    """

    def __init__(self, msg: str) -> None:
        """SeedboxSyncError init."""
        logger.exception(msg)
        sys.exit(msg)


class SeedboxSyncConfigurationError(SeedboxSyncError):
    """
    Exception raised for configuration-related errors.

    This error typically occurs when the configuration file contains
    invalid, missing, or inconsistent settings.
    """


class SyncProtocoleError(SeedboxSyncError):
    """
    Exception raised when an unsupported or misconfigured synchronization protocol
    is specified.
    """


class PingServiceError(SeedboxSyncError):
    """
    Exception raised when an unsupported or misconfigured ping service
    is specified.
    """


class SeedboxsyncConnectionError(SeedboxSyncError):
    """Exception raised when the connection to the remote seedbox fails."""
