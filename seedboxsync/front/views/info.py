# -*- coding: utf-8 -*-
#
# Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
import humanize
from flask import render_template
from peewee import fn
from datetime import datetime
from seedboxsync.core.dao import Download, Lock, SeedboxSync
from seedboxsync.front.cache import cache
from seedboxsync.front.views import bp
from seedboxsync.front.utils import init_flash
from seedboxsync.__version__ import __version__ as version


@bp.route("/info")
@cache.cached(timeout=60)
def info() -> str:
    """
    Information page view.
    """
    init_flash()

    # DL stats
    query_stats = Download.select().where(Download.finished != 0)
    total_files = query_stats.count()
    total_size = sum([d.seedbox_size for d in query_stats if d.seedbox_size])
    sync_blackhole: Lock | bool
    sync_seedbox: Lock | bool

    try:
        sync_blackhole = Lock.get(Lock.key == "sync_blackhole")
    except Lock.DoesNotExist:  # type: ignore[attr-defined]
        sync_blackhole = False
    try:
        sync_seedbox = Lock.get(Lock.key == "sync_seedbox")
    except Lock.DoesNotExist:  # type: ignore[attr-defined]
        sync_seedbox = False

    # First dl stats
    first_date = Download.select(fn.MIN(Download.finished)).where(Download.finished != 0).scalar()
    first_delta = ""
    if first_date is not None:
        first_delta = datetime.now() - first_date
        first_delta = humanize.precisedelta(first_delta, minimum_unit="days")

    info = {
        "stats_total_files": total_files,
        "stats_total_size": humanize.filesize.naturalsize(total_size, True),
        "stats_first": first_date,
        "stats_first_delta": first_delta,
        "version": version,
        "seedboxsync_version": SeedboxSync.get_version(),
        "seedboxsync_db_version": SeedboxSync.get_db_version(),
        "sync_blackhole": sync_blackhole,
        "sync_seedbox": sync_seedbox,
    }

    return render_template("info.html", info=info)
