#
# Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
"""SeedboxSync Flask view for uploaded torrents."""

from flask import render_template
from seedboxsync.front.cache import cache
from seedboxsync.front.login_manager import login_required
from seedboxsync.front.views import bp


@bp.route("/uploaded")
@login_required  # type: ignore[untyped-decorator]
@cache.cached(timeout=300)  # pyright: ignore [reportUntypedFunctionDecorator]
def uploaded() -> str:
    """
    Render the uploaded torrents list view.

    Initializes flash messages and returns the rendered HTML template
    containing the history or status of uploaded torrents (cached for 5 minutes).

    Returns:
        str: Rendered HTML template.
    """
    return render_template("uploaded.html")
