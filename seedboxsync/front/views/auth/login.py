#
# Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
"""SeedboxSync Flask view for authentication handling."""

import datetime
from flask import flash, redirect, render_template, request, url_for
from flask_login import login_user
from werkzeug.wrappers.response import Response
from seedboxsync.core import current_app as app
from seedboxsync.core.dao.user import User
from seedboxsync.core.utils import is_safe_redirect_url
from seedboxsync.front.babel import gettext as _
from seedboxsync.front.forms import LoginForm
from seedboxsync.front.oauth2 import oauth
from seedboxsync.front.views import bp_auth as bp


@bp.route("/login", methods=["GET", "POST"])
def login() -> str | Response:
    """
    Render and process the user login view.

    Authenticates user credentials, logs in the user session upon successful
    validation, and redirects to the requested target URL or homepage.

    Returns:
        str | Response: Rendered login template or HTTP redirect response.
    """
    form = LoginForm()

    # Basic auth
    if form.validate_on_submit():
        login = request.form.get("login") or ""
        password = request.form.get("password") or ""
        next_url = request.args.get("next") or ""
        remember = request.form.get("remember") == "1"

        if not is_safe_redirect_url(next_url):
            next_url = ""

        user = User.authenticate(login, password)

        # User is logged
        if user is not None:
            login_user(user, remember=remember)
            flash(_("Logged in successfully."), "success")

            # Update last login timestamp
            user.last_login = datetime.datetime.now()
            user.save()

            return redirect(next_url or url_for("frontend.homepage"))

        # User is not logged
        flash(_("Invalid username or password."), "danger")

    if request.args.get("provider") == "oauth" and app.seedboxsync_config.get("oauth_enabled"):
        oauth_name = app.seedboxsync_config.get("oauth_name")
        redirect_uri = url_for("auth.authorize", _external=True)
        return oauth.create_client(oauth_name).authorize_redirect(redirect_uri)  # type: ignore[no-any-return]

    return render_template("login.html", form=form)
