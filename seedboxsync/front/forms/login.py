#
# Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
"""SeedboxSync WTForms form for login."""

from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField
from wtforms.validators import DataRequired
from seedboxsync.front.babel import gettext as _


class LoginForm(FlaskForm):  # type: ignore[misc]
    """Login form for user authentication."""

    login = StringField(_("Username or email"), validators=[DataRequired()], render_kw={"placeholder": "admin", "icon": "fa-user"})
    password = PasswordField(_("Password"), validators=[DataRequired()], render_kw={"placeholder": "admin", "icon": "fa-lock"})
