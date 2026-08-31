#
# Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
"""SeedboxSync Flask view for homepage."""

from flask import render_template
from seedboxsync.core import current_app as app
from seedboxsync.front.cache import cache
from seedboxsync.front.login_manager import login_required
from seedboxsync.front.views import bp


@bp.route("/")
@login_required  # type: ignore[untyped-decorator]
@cache.cached(timeout=300)  # pyright: ignore [reportUntypedFunctionDecorator]
def homepage() -> str:
    """
    Render the home page view.

    Initializes flash messages and renders the main dashboard template using
    the active application configuration (cached for 5 minutes).

    Returns:
        str: Rendered HTML template for the home page.
    """
    return render_template("homepage.html", config=app.seedboxsync_config)
