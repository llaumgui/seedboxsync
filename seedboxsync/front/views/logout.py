#
# Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
"""SeedboxSync Flask view for authentication handling."""

from flask import redirect, url_for
from flask_login import logout_user
from werkzeug.wrappers.response import Response
from seedboxsync.front.login_manager import login_required
from seedboxsync.front.views import bp


@bp.route("/logout")
@login_required  # type: ignore[untyped-decorator]
def logout() -> str | Response:
    """
    Log out the current user and redirect to the application homepage.

    Clears the current session through Flask-Login before executing the redirect.

    Returns:
        str | Response: HTTP redirect response targeting the homepage view.
    """
    logout_user()
    return redirect(url_for("frontend.homepage"))
