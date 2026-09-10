#
# Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
"""DAO package with all Peewee models."""

from collections.abc import Iterable
from typing import Any, cast

from seedboxsync.core.database.dao.model import SeedboxSyncModel  # isort: skip
from seedboxsync.core.database.dao.download import Download
from seedboxsync.core.database.dao.seedboxsync import SeedboxSync
from seedboxsync.core.database.dao.taskstatus import TaskStatus
from seedboxsync.core.database.dao.torrent import Torrent
from seedboxsync.core.database.dao.user import User

from seedboxsync.core.database.dao.apikey import ApiKey  # isort: skip

__all__ = ["ApiKey", "Download", "SeedboxSync", "SeedboxSyncModel", "TaskStatus", "Torrent", "User"]


def typed_peewee_dicts(query: Any) -> Iterable[dict[str, Any]]:
    """
    Cast a Peewee query configured with ``dicts()`` to dictionary rows.

    This helper works around Peewee's incomplete type annotations, which may
    still report model instances even when ``dicts()`` is used.

    Args:
        query: A Peewee query configured to return rows as dictionaries.

    Returns:
        An iterable of dictionary-based query results.
    """
    return cast(Iterable[dict[str, Any]], query)


def typed_peewee_dict(query: Any) -> dict[str, Any]:
    """
    Cast a Peewee query configured with ``first()`` (or others) to dictionary rows.

    This helper works around Peewee's incomplete type annotations, which may
    still report model instances even when ``first()`` (or others) is used.

    Args:
        query: A Peewee query configured to return rows as dictionaries.

    Returns:
        An dictionary-based query results.
    """
    return cast(dict[str, Any], query)
