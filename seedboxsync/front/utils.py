#
# Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
"""SeedboxSync front utils module."""

from flask import flash
from seedboxsync.core import current_app


def init_flash() -> None:
    """Initialize flash messages."""
    if current_app.config.get("INIT_ERROR"):
        flash(current_app.config["INIT_ERROR"], "error")
