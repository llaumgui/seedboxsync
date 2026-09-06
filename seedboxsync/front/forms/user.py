#
# Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
"""SeedboxSync WTForms form for user management."""

from flask_wtf import FlaskForm
from wtforms import EmailField, PasswordField, StringField
from wtforms.validators import DataRequired, Length, Optional
from seedboxsync.front.babel import gettext as _


class UserBaseForm(FlaskForm):  # type: ignore[misc]
    """
    Base form for managing core user account details.

    Provides common input fields and data validation rules shared across
    user creation and edition workflows.
    """

    username = StringField(_("Username"), validators=[DataRequired(), Length(min=4, max=25)], render_kw={"placeholder": "admin", "icon": "fa-user"})
    email = EmailField(_("Email"), validators=[DataRequired(), Length(min=8, max=35)], render_kw={"placeholder": "admin", "icon": "fa-user"})


class UserEditForm(UserBaseForm):
    """
    Form for editing existing user account details.

    Extends the base user form with an optional password field to allow
    updating user credentials without forcing a password reset.
    """

    password = PasswordField(_("Password"), validators=[Optional(), Length(min=8, max=128)], render_kw={"placeholder": "••••••••••••", "icon": "fa-lock"})


class UserCreateForm(UserBaseForm):
    """
    Form for creating new user accounts.

    Extends the base user form with a mandatory password field to ensure
    a password is provided during initial account creation.
    """

    password = PasswordField(_("Password"), validators=[DataRequired(), Length(min=8, max=128)], render_kw={"placeholder": "••••••••••••", "icon": "fa-lock"})
