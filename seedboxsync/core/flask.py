# -*- coding: utf-8 -*-
#
# Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
from typing import Any, cast
from flask import current_app, Flask
from seedboxsync.core import Config


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


seedboxsync_current_app = cast(SeedboxSyncFlask, current_app)
