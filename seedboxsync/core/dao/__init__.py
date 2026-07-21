#
# Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
from collections.abc import Iterable
from typing import Any, TypeVar, cast

from seedboxsync.core.dao.model import SeedboxSyncModel  # isort: skip
from seedboxsync.core.dao.download import Download
from seedboxsync.core.dao.seedboxsync import SeedboxSync
from seedboxsync.core.dao.taskstatus import TaskStatus
from seedboxsync.core.dao.torrent import Torrent

__all__ = ["Download", "SeedboxSync", "SeedboxSyncModel", "TaskStatus", "Torrent"]


T = TypeVar("T")


def typed_peewee_dicts[T](query: T) -> Iterable[dict[str, Any]]:
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
