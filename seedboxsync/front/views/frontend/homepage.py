#
# Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
"""SeedboxSync Flask view for homepage."""

from flask import render_template
from seedboxsync.front.cache import cached
from seedboxsync.front.login_manager import login_required
from seedboxsync.front.views import bp_frontend as bp


@bp.route("/")
@cached(timeout=300)  # pyright: ignore [reportUntypedFunctionDecorator]
@login_required  # type: ignore[untyped-decorator]
def homepage() -> str:
    """
    Render the home page view.

    Initializes flash messages and renders the main dashboard template using
    the active application configuration (cached for 5 minutes).

    Returns:
        str: Rendered HTML template for the home page.
    """
    return render_template("homepage.html")
