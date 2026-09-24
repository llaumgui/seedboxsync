#
# Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
"""SeedboxSync Flask view for info."""

from datetime import datetime
from flask import render_template
from humanize import filesize, precisedelta
from peewee import fn
from seedboxsync.__version__ import __version__ as version
from seedboxsync.core import current_app
from seedboxsync.core.database.models import Download, TaskStatus
from seedboxsync.front.cache import cache
from seedboxsync.front.login_manager import login_required
from seedboxsync.front.views import bp_settings as bp


@bp.route("/info")
@bp.route("")
@login_required  # type: ignore[untyped-decorator]
def info() -> str:
    """
    Render the system information view.

    Gathers download metrics, system task statuses, database versioning,
    and application runtime statistics (cached for 60 seconds).

    Returns:
        str: Rendered HTML template containing overall application information.
    """
    return render_template("settings/info.html", info=_get_info_data())


@cache.memoize(timeout=60)
def _get_info_data() -> dict[str, object]:
    """
    Fetch and calculate application system information.

    Queries download metrics, background task statuses, application version,
    and database migration metadata. Cached for 60 seconds.

    Returns:
        dict[str, object]: Dictionary containing gathered system statistics
            and status flags.
    """
    # Download statistics
    query_stats = Download.select().where(Download.finished != 0)
    total_files = query_stats.count()
    total_size = sum([d.seedbox_size for d in query_stats if d.seedbox_size])
    sync_blackhole: TaskStatus | bool
    sync_seedbox: TaskStatus | bool

    # Get statues
    keys = ["sync-blackhole", "sync-seedbox", "heartbeat"]
    statuses = {ts.key: ts for ts in TaskStatus.select().where(TaskStatus.key.in_(keys))}
    sync_blackhole = statuses.get("sync-blackhole", False)
    sync_seedbox = statuses.get("sync-seedbox", False)
    heartbeat = statuses.get("heartbeat", False)

    # First download statistics
    first_date = Download.select(fn.MIN(Download.finished)).where(Download.finished != 0).scalar()
    first_delta = ""
    if first_date is not None:
        first_delta = datetime.now() - first_date
        first_delta = precisedelta(first_delta, minimum_unit="days")

    return {
        "stats_total_files": total_files,
        "stats_total_size": filesize.naturalsize(total_size, True),
        "stats_first": first_date,
        "stats_first_delta": first_delta,
        "version": version,
        "last_migration": current_app.config.get("LAST_MIGRATION"),
        "sync_blackhole": sync_blackhole,
        "sync_seedbox": sync_seedbox,
        "heartbeat": heartbeat,
    }
