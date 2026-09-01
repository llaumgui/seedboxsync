#
# Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
"""SeedboxSync front cache module."""

from collections.abc import Callable
from typing import Any
from flask import request, session
from flask_caching import Cache
from flask_login import current_user
from seedboxsync.core import current_app as app

# Global Flask-Caching instance
cache = Cache()


def make_user_cache_key() -> str:
    """
    Generate a dynamic cache key based on the user's authentication state[cite: 1].

    Appends the authenticated user ID or an 'anonymous' flag to the request path
    to ensure cached responses are segregated between logged-in and anonymous sessions.

    Returns:
        str: Generated cache key combining the request path and user status.
    """
    if app.config["LOGIN_DISABLED"]:
        return f"{request.path}_login_disabled"

    user_status = f"user_{current_user.id}" if current_user.is_authenticated else "anonymous"
    return f"{request.path}_{user_status}"


def cached(timeout: int = 300) -> Callable[..., Any]:
    """
    Custom cached decorator enforcing user-aware cache keys.

    Args:
        timeout (int): Cache expiration timeout in seconds. Defaults to 300.

    Returns:
        Callable[..., Any]: Flask-Caching cached decorator configured with make_user_cache_key.
    """
    return cache.cached(make_cache_key=make_user_cache_key, timeout=timeout, unless=lambda: bool(session.get("_flashes")))
