#
# Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
"""SeedboxSync Flask view for login."""

from flask import flash, redirect, render_template, request, url_for
from flask_login import login_user
from werkzeug.wrappers.response import Response
from seedboxsync.core.dao.user import User
from seedboxsync.front.forms import LoginForm
from seedboxsync.front.views import bp


@bp.route("/login", methods=["GET", "POST"])
def login() -> str | Response:
    """Login view."""
    form = LoginForm()
    if form.validate_on_submit():
        login = request.form.get("login") or ""
        password = request.form.get("password") or ""
        next_url = request.args.get("next") or ""

        user = User.authenticate(login, password)
        login_user(user)

        flash("Logged in successfully.")
        return redirect(next_url or url_for("index"))

    return render_template("login.html", form=form)
