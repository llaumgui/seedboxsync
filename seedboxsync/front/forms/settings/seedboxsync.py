#
# Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
"""SeedboxSync WTForms form for settings SeedboxSync."""

from flask_wtf import FlaskForm
from wtforms import BooleanField, SelectField
from seedboxsync.front.babel import ALLOWED_LANGUAGES, gettext as _


class SettingsSeedboxSyncForm(FlaskForm):  # type: ignore[misc]
    """
    Form for configuring core SeedboxSync preferences.

    Provides controls for toggling background synchronization tasks and
    customizing WebUI presentation settings (theme and language).
    """

    sync_blackhole_enabled = BooleanField(_("Enable the blackhole synchronization task"))
    sync_seedbox_enabled = BooleanField(_("Enable the seedbox synchronization task"))
    webui_theme = SelectField(
        _("Theme of the WebUI"),
        choices=[
            ("auto", _("Automatic")),
            ("dark", _("Dark")),
            ("light", _("Light")),
        ],
        default="auto",
    )
    webui_language = SelectField(
        _("Language of the WebUI"),
        choices=[("auto", _("Automatic"))] + [(lang, lang) for lang in ALLOWED_LANGUAGES],
        default="auto",
    )
    wtf_csrf_enabled = BooleanField(_("Enable CSRF protection for all forms?"))
