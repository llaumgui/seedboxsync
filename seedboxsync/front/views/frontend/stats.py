#
# Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
"""SeedboxSync Flask view for stats."""

from flask import render_template
from humanize import filesize
from seedboxsync.core.dao import Download
from seedboxsync.front.cache import cached
from seedboxsync.front.login_manager import login_required
from seedboxsync.front.views import bp_frontend as bp


@bp.route("/stats")
@cached(timeout=300)  # pyright: ignore [reportUntypedFunctionDecorator]
@login_required  # type: ignore[untyped-decorator]
def stats() -> str:
    """
    Render the statistics view.

    Calculates the total number of finished downloads and their cumulative file
    size, formats the size in human-readable format, and renders the stats page
    (cached for 5 minutes).

    Returns:
        str: Rendered HTML template containing the summary statistics.
    """
    query = Download.select().where(Download.finished != 0)
    total_files = query.count()
    total_size = sum([d.seedbox_size for d in query if d.seedbox_size])

    stats_total = {
        "files": total_files,
        "total_size": filesize.naturalsize(total_size, True),
    }

    return render_template("stats.html", stats_total=stats_total)
