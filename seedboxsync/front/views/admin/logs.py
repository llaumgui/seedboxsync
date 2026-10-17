#
# Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
"""SeedboxSync Flask view for info."""

from flask import render_template
from seedboxsync.front.login_manager import admin_required
from seedboxsync.front.views import bp_admin as bp


@bp.route("/logs")
@admin_required
def logs() -> str:
    """
    Render the system information view.

    Gathers download metrics, system task statuses, database versioning,
    and application runtime statistics (cached for 60 seconds).

    Returns:
        str: Rendered HTML template containing overall application information.
    """
    return render_template(
        "admin/logs.html",
    )
