# -*- coding: utf-8 -*-
#
# Copyright (C) 2015-2025 Guillaume Kulakowski <guillaume@kulakowski.fr>
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

import sys
from cement import minimal_logger  # type: ignore[attr-defined]

# Initialize a minimal Cement logger for error reporting
LOG = minimal_logger(__name__)


class SeedboxSyncError(Exception):
    """
    Base exception class for all SeedboxSync errors.

    When raised, this exception logs the error message and terminates
    the program immediately. It is intended for unrecoverable errors
    that prevent normal operation.

    Args:
        str msg: The error message to log and display before exiting.
    """

    def __init__(self, msg: str) -> None:
        LOG.error(msg)
        sys.exit(msg)


class SeedboxSyncConfigurationError(SeedboxSyncError):
    """
    Exception raised for configuration-related errors.

    This error typically occurs when the configuration file contains
    invalid, missing, or inconsistent settings.
    """
    pass
