#
# Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
"""SeedboxSync WTForms form for authentication settings."""

from flask_wtf import FlaskForm
from wtforms import BooleanField
from seedboxsync.front.babel import gettext as _


class SettingsAuthenticationForm(FlaskForm):  # type: ignore[misc]
    """
    Form for configuring authentication settings.

    Provides administrative controls for enabling or disabling global
    user authentication within the application.
    """

    login_disabled = BooleanField(_("Disabled the authentication?"))
    auth_gravatar_enabled = BooleanField(_("Enable Gravatar for users?"))
