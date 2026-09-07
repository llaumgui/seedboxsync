#
# Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
"""WTForms definitions for API key management."""

from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired, Length
from seedboxsync.front.babel import gettext as _


class ApiKeyForm(FlaskForm):  # type: ignore[misc]
    """
    Form for creating a new API key.

    Requires a descriptive name/label for identifying the key's usage context.
    """

    name = StringField(_("API key Name"), validators=[DataRequired(), Length(min=4, max=32)], render_kw={"placeholder": "homeassistant", "icon": "fa-key"})
