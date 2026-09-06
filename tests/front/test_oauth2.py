from unittest.mock import patch
from seedboxsync.front.oauth2 import init_oauth2


def test_init_oauth2_does_not_register_provider_when_disabled(app):
    app.config["SEEDBOXSYNC_OAUTH_ENABLED"] = False

    with patch("seedboxsync.front.oauth2.oauth.init_app") as init_app, patch("seedboxsync.front.oauth2.oauth.register") as register:
        init_oauth2(app)

    init_app.assert_not_called()
    register.assert_not_called()


def test_init_oauth2_registers_provider_with_configured_options(app):
    app.config.update(
        {
            "SEEDBOXSYNC_OAUTH_ENABLED": True,
            "SEEDBOXSYNC_OAUTH_NAME": "oidc",
            "SEEDBOXSYNC_OAUTH_CLIENT_ID": "client-id",
            "SEEDBOXSYNC_OAUTH_CLIENT_SECRET": "client-secret",
            "SEEDBOXSYNC_OAUTH_SERVER_METADATA_URL": "https://issuer.example/.well-known/openid-configuration",
        }
    )

    with patch("seedboxsync.front.oauth2.oauth.init_app") as init_app, patch("seedboxsync.front.oauth2.oauth.register") as register:
        init_oauth2(app)

    init_app.assert_called_once_with(app)
    register.assert_called_once_with(
        name="oidc",
        client_id="client-id",
        client_secret="client-secret",
        server_metadata_url="https://issuer.example/.well-known/openid-configuration",
        client_kwargs={
            "scope": "openid profile email",
            "code_challenge_method": "S256",
            "token_endpoint_auth_method": "client_secret_post",
        },
    )
