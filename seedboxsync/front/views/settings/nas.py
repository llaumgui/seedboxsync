#
# Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
"""SeedboxSync Flask view for settings NAS."""

from flask import flash, render_template
from seedboxsync.core import current_app as app
from seedboxsync.front.babel import gettext as _
from seedboxsync.front.forms import SettingsNasForm
from seedboxsync.front.login_manager import login_required
from seedboxsync.front.utils import save_settings_form
from seedboxsync.front.views import bp_settings as bp


@bp.route("/settings/nas", methods=("GET", "POST"))
@login_required  # type: ignore[untyped-decorator]
def nas() -> str:
    """
    Render and process the NAS storage settings form.

    Configures local destination paths and storage parameters.

    Returns:
        str: Rendered HTML template for the NAS settings page.
    """
    form = SettingsNasForm(data=app.seedboxsync_config)

    if form.validate_on_submit():
        try:
            save_settings_form(form)
            flash(_("Configuration saved successfully."), "success")
        except Exception as e:
            app.logger.exception("Failed to save configuration.", exc_info=e)
            flash(_("Failed to save configuration."), "danger")

    return render_template("settings/nas.html", form=form)
