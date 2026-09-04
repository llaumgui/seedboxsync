#
# Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
"""SeedboxSync front OAuth module."""

from authlib.integrations.flask_client import OAuth
from seedboxsync.core import Flask

# Global OAuth client instance
oauth = OAuth()


def init_oauth2(app: Flask) -> None:
    """
    Initialize OAuth and register configured authentication providers with Flask.

    Checks application configuration for enabled OAuth/OIDC settings and registers
    the external OpenID Connect identity provider using Authlib integration.

    Args:
        app (Flask): The target Flask application instance.
    """
    oauth._registry.clear()
    oauth._clients.clear()

    # Verify if OAuth provider authentication is enabled in application configuration
    if app.seedboxsync_config.get("oauth_enabled"):
        # Bind Authlib extension to Flask app lifecycle
        oauth.init_app(app)

        # Register remote OIDC provider with configured OAuth client credentials
        oauth.register(
            name=app.seedboxsync_config.get("oauth_name"),
            client_id=app.seedboxsync_config.get("oauth_client_id"),
            client_secret=app.seedboxsync_config.get("oauth_client_secret"),
            server_metadata_url=app.seedboxsync_config.get("oauth_server_metadata_url"),
            client_kwargs={
                "scope": "openid profile email",
                "code_challenge_method": "S256",
                "token_endpoint_auth_method": "client_secret_post",
            },
        )
        app.logger.debug(
            "OAuth provider '%s' (%s) registered successfully with client_id '%s'.",
            app.seedboxsync_config.get("oauth_name"),
            app.seedboxsync_config.get("oauth_server_metadata_url"),
            app.seedboxsync_config.get("oauth_client_id")
        )
