#
# Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
"""SeedboxSync Flask view for authentication handling."""

from flask import redirect, render_template, request, url_for
from flask_login import login_user
from werkzeug.wrappers.response import Response
from seedboxsync.core import current_app
from seedboxsync.core.database.models.user import User
from seedboxsync.front.babel import gettext as _
from seedboxsync.front.forms import LoginForm
from seedboxsync.front.oauth2 import oauth
from seedboxsync.front.utils import is_safe_redirect_url, toast
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
    # Auto redirect to OAuth2 provider if OAuth is enabled and built-in authentication is disabled
    oauth_builtin_authentication_disabled = current_app.seedboxsync_config.get("oauth_builtin_authentication_disabled", False)
    oauth_enabled = current_app.seedboxsync_config.get("oauth_enabled", False)
    if oauth_builtin_authentication_disabled and oauth_enabled:
        return __authorize_redirect()

    if request.args.get("provider") == "oauth2" and current_app.seedboxsync_config.get("oauth_enabled"):
        return __authorize_redirect()

    form = LoginForm()

    # Basic auth
    if form.validate_on_submit():
        login = request.form.get("login") or ""
        password = request.form.get("password") or ""
        next_url = request.args.get("next")
        remember = request.form.get("remember") == "1"

        user = User.authenticate(login, password)

        # User is logged
        if user is not None:
            login_user(user, remember=remember)
            toast(_("Logged in successfully."), _("Login"), "success")

            # Sanitization/Validation for SonarQube (Open Redirect protection)
            target_url = url_for("frontend.homepage")
            if next_url and is_safe_redirect_url(next_url):
                target_url = next_url

            return redirect(target_url)

        # User is not logged
        toast(_("Invalid username or password."), _("Login"), "danger")

    return render_template("login.html", form=form)


def __authorize_redirect() -> Response:
    """
    Redirect the user to the configured OAuth/OIDC provider's authorization URL.

    Obtains the registered OAuth client name from application settings, builds
    the external redirect URI, and initiates the OIDC authorization flow.

    Returns:
        Response: Flask redirect response object targeting the identity provider.
    """
    # Retrieve OAuth client name and construct absolute callback URL
    oauth_name = current_app.seedboxsync_config.get("oauth_name")
    redirect_uri = url_for("auth.authorize", _external=True)

    # Initiate authorization redirect via Authlib client
    return oauth.create_client(oauth_name).authorize_redirect(redirect_uri)  # type: ignore[no-any-return]
