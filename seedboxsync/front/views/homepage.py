#
# Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
"""SeedboxSync Flask vierw for homepage."""
from flask import render_template
from seedboxsync.core import current_app as app
from seedboxsync.front.cache import cache
from seedboxsync.front.utils import init_flash
from seedboxsync.front.views import bp


@bp.route("/")
@cache.cached(timeout=300)
def homepage() -> str:
    """Home page view."""
    init_flash()

    return render_template("homepage.html", config=app.seedboxsync_config)
