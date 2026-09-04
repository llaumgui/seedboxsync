#
# Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
"""SeedboxSync WTForms form for user management."""

from flask_wtf import FlaskForm
from wtforms import EmailField, PasswordField, StringField
from wtforms.validators import DataRequired, Length
from seedboxsync.front.babel import gettext as _


class UserForm(FlaskForm):  # type: ignore[misc]
    """
    Form for managing user account details.

    Provides input fields and basic data validation for editing or
    creating application users.
    """

    username = StringField(_("Username"), validators=[DataRequired(), Length(min=4, max=25)], render_kw={"placeholder": "admin", "icon": "fa-user"})
    email = EmailField(_("Email"), validators=[DataRequired(), Length(min=8, max=35)], render_kw={"placeholder": "admin", "icon": "fa-user"})
    password = PasswordField(_("Password"), validators=[DataRequired(), Length(min=8, max=256)], render_kw={"placeholder": "admin", "icon": "fa-lock"})
