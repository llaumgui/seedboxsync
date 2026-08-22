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
from seedboxsync.front.utils import init_flash
from seedboxsync.front.views import bp


@bp.route("/uploaded")
@login_required  # type: ignore[untyped-decorator]
@cache.cached(timeout=300)  # pyright: ignore [reportUntypedFunctionDecorator]
def uploaded() -> str:
    """Uploaded list view."""
    init_flash()

    return render_template("uploaded.html")
