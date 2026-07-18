# -*- coding: utf-8 -*-
#
# Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
"""
A collection of utility functions for SeedboxSync.
"""

import os
from pathlib import Path
from bcoding import bdecode
from flask import current_app as app
from urllib.parse import urlparse


def byte_to_gi(bytes_value: float, suffix: str = "B") -> str:
    """
    Convert in human readable units.

    Args:
        bytes_value (integer): Value not human readable.
        suffix (str): Suffix for value given to (default: B).

    Returns:
        str: human readable value in Gi.
    """
    gib = bytes_value / (1024**3)
    return f"{gib:.1f}Gi{suffix}"


def get_torrent_infos(torrent_path: str) -> None | str:
    """
    Extracts information from a torrent file.

    Args:
        torrent_path (str): Path to the torrent file.

    Returns:
        str: Decoded torrent information.

    Raises:
        Exception: If the file is not a valid torrent.
    """
    with open(torrent_path, "rb") as torrent:
        torrent_info = None

        try:
            torrent_info = bdecode(torrent.read())
        except Exception as exc:
            app.logger.error('Not valid torrent: "%s"' + str(exc))
        finally:
            torrent.close()

        return torrent_info


def is_running_in_docker() -> bool:
    """
    Return whether the current process appears to run inside Docker.

    Returns:
        bool: True if in docker envoronment.

    """
    # Test mountinfo
    if os.path.exists("/proc/self/mountinfo"):
        with open("/proc/self/mountinfo", "r") as f:
            if "docker" in f.read() or "overlay" in f.read():
                return True

    # Test du cgroup
    if os.path.exists("/proc/1/cgroup"):
        with open("/proc/1/cgroup", "r") as f:
            lines = f.read()
            if "docker" in lines or "kubepods" in lines:
                return True

    # Test /.dockerenv but not on podman
    return Path("/.dockerenv").exists()


def get_web_healthcheck_url() -> str:
    """
    Return the URL used to check the local Flask application.

    Returns:
        str: The healthcheck URL.
    """

    explicit_url = os.getenv("HEALTHCHECK_URL")
    if explicit_url:
        return explicit_url.rstrip("/") + "/healthcheck"

    bind = os.getenv("BIND")
    if bind:
        return _healthcheck_url_from_bind(bind)

    port = 8000 if is_running_in_docker() else 5000
    return f"http://127.0.0.1:{port}/healthcheck"


def _healthcheck_url_from_bind(bind: str) -> str:
    """
    Build a local healthcheck URL from a Gunicorn bind value.

    Returns:
        str: The healthcheck URL from BIND.
    """

    bind = bind.strip()

    if bind.startswith("unix:"):
        raise ValueError("A Unix socket bind cannot be checked with a standard HTTP URL.")

    # urlparse requires a scheme to correctly parse host and port.
    parsed = urlparse(f"//{bind}")

    if parsed.port is None:
        raise ValueError(f"Invalid BIND value: {bind}")

    host = parsed.hostname or "127.0.0.1"

    if host in {"0.0.0.0", "::", "[::]"}:
        host = "127.0.0.1"

    return f"http://{host}:{parsed.port}/healthcheck"
