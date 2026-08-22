#
# Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
"""SeedboxSync Flask view for login."""

from flask import render_template
from werkzeug.wrappers.response import Response
from seedboxsync.core.dao import User
from seedboxsync.front.views import bp


@bp.route("/settings/users", methods=["GET", "POST"])
def settings_users() -> str | Response:
    """Users list view."""
    users = User.select(
        User.username,
        User.email,
        User.created,
        User.last_login
    )

    return render_template("settings/users.html", users=users)
