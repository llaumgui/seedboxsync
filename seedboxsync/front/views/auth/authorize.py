#
# Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
"""SeedboxSync Flask view for authentication handling."""

import datetime
from flask import flash, redirect, url_for
from flask_login import login_user
from werkzeug.wrappers.response import Response
from seedboxsync.core import current_app as app
from seedboxsync.core.dao.user import User
from seedboxsync.front.babel import gettext as _
from seedboxsync.front.oauth2 import oauth
from seedboxsync.front.views import bp_auth as bp

view_login = "auth.login"

@bp.route("/oauth2/oidc/callback")
def authorize() -> Response:
    """
    Process OAuth authorization callback.

    Exchanges authorization code for tokens, retrieves user information,
    synchronizes or creates the local user entity, and logs the user in.

    Returns:
        Response: HTTP redirect to homepage or error destination.
    """
    try:
        # Get client name from configuration and create OAuth client
        oauth_name = app.seedboxsync_config.get("oauth_name")
        client = oauth.create_client(oauth_name)
        if client is None:
            flash(_("OAuth provider is not properly configured."), "danger")
            return redirect(url_for(view_login))

        # Get token and user info from OAuth provider
        token = client.authorize_access_token()
        user_info = client.userinfo(token=token)
        app.logger.debug("OAuth user info retrieved: %s", user_info)
        email = user_info.get("email")
        username = (
            user_info.get("preferred_username")
            or user_info.get("name")
            or email
        )
        if not email:
            flash(_("Failed to obtain email from OAuth provider."), "danger")
            return redirect(url_for(view_login))

        # Check if user exists or create a new one based on configuration
        if app.seedboxsync_config.get("oauth_auto_create_user"):
            user, _created = User.get_or_create(email=email, defaults={"username": username})  # type: ignore[no-untyped-call]
        else:
            user = User.get(User.email == email)

        # Connect user with Flask-Login
        login_user(user)
        flash(_("Logged in successfully."), "success")

        # Update last login timestamp
        user.last_login = datetime.datetime.now()
        user.save()

        return redirect(url_for("frontend.homepage"))

    except Exception as e:
        app.logger.error("Authentication failed: %s", str(e))
        flash(_("Authentication failed. Please try again."), "danger")
        return redirect(url_for(view_login))
