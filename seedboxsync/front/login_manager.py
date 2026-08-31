#
# Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
"""SeedboxSync login manager module using Flask-Login."""

from typing import Any
from flask import Request, Response, abort, redirect, request, url_for
from flask_login import LoginManager, login_required as flask_login_required
from seedboxsync.core.dao import User
from seedboxsync.front.babel import gettext as _

# Setup Flask-Login
login_manager = LoginManager()
login_manager.login_view = "frontend.login"  # pyright: ignore[reportAttributeAccessIssue]
login_manager.login_message = _("Please log in to access this page.")
login_manager.login_message_category = "info"


@login_manager.user_loader  # type: ignore[untyped-decorator]
def load_user(user_id: str) -> "User | None":
    """Load a user by their ID."""
    return User.get(user_id)


@login_manager.unauthorized_handler  # type: ignore[untyped-decorator]
def unauthorized() -> Any | int | Response:
    """Setup unauthorized_handler for API."""
    if request.blueprint == "api":
        abort(401)

    # Default behavior for the frontend
    return redirect(url_for("frontend.login", next=request.path))


@login_manager.request_loader  # type: ignore[untyped-decorator]
def load_user_from_request(request: Request) -> "User | None":
    """Load and authenticate a user from HTTP Basic authentication."""
    auth = request.authorization
    if auth is None or auth.type != "basic":
        return None
    if auth.username is None or auth.password is None:
        return None

    try:
        user = User.authenticate(auth.username, auth.password)
    except User.DoesNotExist:  # pyright: ignore[reportAttributeAccessIssue]
        return None

    return user


login_required = flask_login_required
