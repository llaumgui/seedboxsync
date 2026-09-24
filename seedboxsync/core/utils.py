#
# Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
"""A collection of utility functions for SeedboxSync."""

import mimetypes
import os
from os import PathLike
from pathlib import Path
from typing import Any
from urllib.parse import urlparse
from bcoding import bdecode
from flask import current_app
import puremagic


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


def ensure_dir_exists(path: str | PathLike[str]) -> None:
    """
    Ensure the directory ``path`` exists, and if not create it.

    Args:
        path (str): The filesystem path of a directory.

    Raises:
        AssertionError: If the directory ``path`` exists, but is not a directory.

    """
    path = Path(path).expanduser().resolve()

    if path.exists() and not path.is_dir():
        raise AssertionError(f"Path `{path}` exists but is not a directory!")
    if not path.exists():
        path.mkdir()


def get_torrent_infos(torrent_path: str | PathLike[str]) -> Any | None:
    """
    Extracts information from a torrent file.

    Args:
        torrent_path (str | PathLike[str]): Path to the torrent file.

    Returns:
        str: Decoded torrent information.

    Raises:
        Exception: If the file is not a valid torrent.
    """
    with Path(torrent_path).open("rb") as torrent:
        torrent_info = None

        try:
            torrent_info = bdecode(torrent.read())
        except Exception:
            current_app.logger.exception("Not valid torrent")
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
    if Path("/proc/self/mountinfo").exists():
        with Path("/proc/self/mountinfo").open() as f:
            if "docker" in f.read() or "overlay" in f.read():
                return True

    # Test du cgroup
    if Path("/proc/1/cgroup").exists():
        with Path("/proc/1/cgroup").open() as f:
            lines = f.read()
            if "docker" in lines or "kubepods" in lines:
                return True

    # Test /.dockerenv but not on podman
    return Path("/.dockerenv").exists()


def get_database_path_from_paths() -> Path:
    """
    Find and return an existing writable database file path.

    Iterates through a predefined list of standard locations to locate a valid
    database file. Returns the first path that exists, is a regular file, and
    has write permissions. If no match is found, falls back to the default
    user configuration path.

    Returns:
        Path: The resolved writable database path if found; otherwise, the default
            path (~/.config/seedboxsync/seedboxsync.db).
    """
    db_paths = [
        Path("~/.config/seedboxsync/seedboxsync.db").expanduser().resolve(),
        Path("~/.seedboxsync.db").expanduser().resolve(),
        Path("~/.seedboxsync/config/seedboxsync.db").expanduser().resolve(),
        Path("/etc/seedboxsync/seedboxsync.db"),
    ]
    for path in db_paths:
        if path.exists() and path.is_file() and os.access(path, os.W_OK):
            return path
    return db_paths[0]


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


def get_mime_type_from_file(filename: str) -> tuple[str, str, str]:
    """
    Detect the MIME type and extension of a file.

    Args:
        filename: Name to the local file to analyze
    Returns:
        tuple[str, str, str]: (mime_type, mime_extension, confidence)
    """
    # Initialize local file path
    local_filepath = Path(current_app.seedboxsync_config.get("local_download_path", "")).expanduser().resolve() / filename  # type: ignore[attr-defined]

    # Use first magic_file
    try:
        current_app.logger.debug(f"Attempting MIME detection via puremagic header analysis for: {local_filepath}")
        results = puremagic.magic_file(local_filepath)
        if results:
            match = results[0]

            mime_extension = match.extension.lstrip(".")
            mime_type = match.mime_type
            mime_confidence = f"puremagic (confidence: {match.confidence})"
            current_app.logger.debug(f"Successfully detected MIME via puremagic: type={mime_type}, ext={mime_extension}, confidence={mime_confidence}")

            return mime_type, mime_extension, mime_confidence

    except (FileNotFoundError, puremagic.PureError):
        pass

    # Fallback with mimetypes
    current_app.logger.debug(f"Attempting MIME detection fallback via mimetypes for: {local_filepath}")
    mime_type, _ = mimetypes.guess_type(local_filepath)

    if mime_type:
        extension = mimetypes.guess_extension(mime_type) or ""
        mime_extension = extension.lstrip(".")
        mime_confidence = "mimetypes (path_fallback)"

        current_app.logger.debug(f"MIME detection completed using fallback: type={mime_type}, ext={mime_extension}, confidence={mime_confidence}")

        return mime_type, mime_extension, "mimetypes (path_fallback)"

    # Last resort when nothing can be detected.
    parts = str(local_filepath).rsplit(".", 1) if local_filepath else []
    mime_extension = parts[1].lower() if len(parts) > 1 else "unknown"

    return "application/octet-stream", mime_extension, "unknown"


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
