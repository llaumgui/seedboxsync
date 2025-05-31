# -*- coding: utf-8 -*-
#
# Copyright (C) 2015-2025 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#

import sys
from cement import minimal_logger

LOG = minimal_logger(__name__)


class SeedboxSyncError(Exception):
    """
    Generic errors.
    """

    def __init__(self, msg: str):
        LOG.error(msg)
        sys.exit(self)


class SeedboxSyncConfigurationError(SeedboxSyncError):
    pass
