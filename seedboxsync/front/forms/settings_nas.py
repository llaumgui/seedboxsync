#
# Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
"""SeedboxSync WTForms form for settings NAS."""

from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired
from seedboxsync.front.babel import gettext as _


class SettingsNasForm(FlaskForm):  # type: ignore[misc]
    """Form for settings NAS."""

    local_watch_path = StringField(
        _("Watch path"),
        validators=[DataRequired()],
        render_kw={"placeholder": "/watch", "icon": "fa-folder", "help": _("Your local watch folder.")},
    )
    local_download_path = StringField(
        _("Downloads path"),
        validators=[DataRequired()],
        render_kw={"placeholder": "/downloads", "icon": "fa-cfolder", "help": _("Path where files are downloaded.")},
    )
