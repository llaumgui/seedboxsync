#
# Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
"""SeedboxSync WTForms form for authentication settings."""

from flask_wtf import FlaskForm
from wtforms import BooleanField, StringField, URLField
from wtforms.validators import Length
from seedboxsync.front.babel import gettext as _


class SettingsAuthenticationForm(FlaskForm):  # type: ignore[misc]
    """
    Form for configuring authentication settings.

    Provides administrative controls for enabling or disabling global
    user authentication within the application.
    """

    login_disabled = BooleanField(_("Disable authentication fully?"))
    auth_gravatar_enabled = BooleanField(_("Enable Gravatar for users?"))

    # OAuth
    oauth_enabled = BooleanField(_("Enable OAuth for the authentication?"))
    oauth_auto_create_user = BooleanField(_("Auto-create users?"))
    oauth_disable_builtin_authentication = BooleanField(_("Disable built-in authentication?"))
    oauth_name = StringField(_("OAuth Client Name"), validators=[Length(min=4, max=32)], render_kw={"placeholder": "oidc", "icon": "fa-tag"})
    oauth_client_id = StringField(_("OAuth Client ID"), render_kw={"placeholder": "fddd434e-fc50-42ec-9b97-69517a7412fc", "icon": "fa-id-badge"})
    oauth_client_secret = StringField(_("OAuth Client Secret"), render_kw={"placeholder": "05e20c6e-2c69-4501-919f-4f44be05ac0b", "icon": "fa-key"})
    oauth_server_metadata_url = URLField(_("OAuth Server Metadata URL"), render_kw={"placeholder": "05e20c6e-2c69-4501-919f-4f44be05ac0b", "icon": "fa-link"})
