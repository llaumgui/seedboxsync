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
from seedboxsync.core.dao import Download, SeedboxSync, TaskStatus
from seedboxsync.front.cache import cached
from seedboxsync.front.login_manager import login_required
from seedboxsync.front.views import bp_frontend as bp


@bp.route("/info")
@cached(timeout=60)  # pyright: ignore [reportUntypedFunctionDecorator]
@login_required  # type: ignore[untyped-decorator]
def info() -> str:
    """
    Render the system information view.

    Gathers download metrics, system task statuses, database versioning,
    and application runtime statistics (cached for 60 seconds).

    Returns:
        str: Rendered HTML template containing overall application information.
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

    info = {
        "stats_total_files": total_files,
        "stats_total_size": filesize.naturalsize(total_size, True),
        "stats_first": first_date,
        "stats_first_delta": first_delta,
        "version": version,
        "seedboxsync_db_version": SeedboxSync.get_db_version(),
        "sync_blackhole": sync_blackhole,
        "sync_seedbox": sync_seedbox,
        "heartbeat": heartbeat,
    }

    return render_template("info.html", info=info)
