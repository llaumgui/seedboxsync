#
# Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
"""SeedboxSync Flask view for settings authentication."""

from flask import flash, render_template
from seedboxsync.core import current_app as app
from seedboxsync.front.babel import gettext as _
from seedboxsync.front.forms import SettingsAuthenticationForm
from seedboxsync.front.login_manager import login_required
from seedboxsync.front.oauth2 import init_oauth2
from seedboxsync.front.utils import save_settings_form
from seedboxsync.front.views import bp_settings as bp


@bp.route("/authentication", methods=("GET", "POST"))
@login_required  # type: ignore[untyped-decorator]
def authentication() -> str:
    """
    Render and process the authentication configuration form.

    Manages access control and authentication provider settings.

    Returns:
        str: Rendered HTML template for the authentication settings page.
    """
    form = SettingsAuthenticationForm(data=app.seedboxsync_config)

    app.logger.info(app.seedboxsync_config)
    if form.validate_on_submit():
        try:
            save_settings_form(form)
            init_oauth2(app)
            flash(_("Configuration saved successfully."), "toast-success")
        except Exception as e:
            app.logger.exception("Failed to save configuration.", exc_info=e)
            flash(_("Failed to save configuration."), "toast-danger")

    return render_template("settings/authentication.html", form=form)
