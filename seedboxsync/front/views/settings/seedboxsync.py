#
# Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
"""SeedboxSync Flask view for settings seedboxsync."""

from flask import render_template
from seedboxsync.core import current_app
from seedboxsync.front.babel import gettext as _
from seedboxsync.front.forms import SettingsSeedboxSyncForm
from seedboxsync.front.login_manager import login_required
from seedboxsync.front.utils import save_settings_form, toast
from seedboxsync.front.views import bp_settings as bp


@bp.route("/seedboxsync", methods=("GET", "POST"))
@login_required  # type: ignore[untyped-decorator]
def seedboxsync() -> str:
    """
    Render and process the general SeedboxSync settings form.

    Handles loading, displaying, and persisting application-wide
    configuration choices.

    Returns:
        str: Rendered HTML template for the main settings page.
    """
    form = SettingsSeedboxSyncForm(data=current_app.seedboxsync_config)

    if form.validate_on_submit():
        try:
            save_settings_form(form)
            toast(_("Configuration saved successfully."), _("SeedboxSync"), "success")
        except Exception as e:
            current_app.logger.exception("Failed to save configuration.", exc_info=e)
            toast(_("Failed to save configuration."), _("SeedboxSync"), "danger")

    return render_template("settings/seedboxsync.html", form=form)
