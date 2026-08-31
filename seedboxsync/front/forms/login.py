#
# Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
"""SeedboxSync WTForms form for login."""

from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField
from wtforms.validators import DataRequired, Length
from seedboxsync.front.babel import gettext as _


class LoginForm(FlaskForm):  # type: ignore[misc]
    """
    Form for user login authentication.

    Provides input fields for username/email and password credentials.
    """

    login = StringField(_("Username or email"), validators=[DataRequired(), Length(min=4, max=35)], render_kw={"placeholder": "admin", "icon": "fa-user"})
    password = PasswordField(_("Password"), validators=[DataRequired(), Length(min=8, max=128)], render_kw={"placeholder": "**********", "icon": "fa-lock"})
