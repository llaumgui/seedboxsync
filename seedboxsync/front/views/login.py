#
# Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
"""SeedboxSync Flask view for authentication handling."""

from flask import flash, redirect, render_template, request, url_for
from flask_login import login_user
from werkzeug.wrappers.response import Response
from seedboxsync.core.dao.user import User
from seedboxsync.core.utils import is_safe_redirect_url
from seedboxsync.front.babel import gettext as _
from seedboxsync.front.forms import LoginForm
from seedboxsync.front.views import bp


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
            return redirect(next_url or url_for("frontend.homepage"))

        # User is not logged
        flash(_("Invalid username or password."), "danger")

    return render_template("login.html", form=form)
