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

from bcoding import bdecode
from flask import current_app as app


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
