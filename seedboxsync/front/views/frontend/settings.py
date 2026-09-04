#
# Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
"""SeedboxSync Flask view for settings."""

from typing import Any
from flask import flash, render_template, request
from flask_wtf import FlaskForm
from seedboxsync.core import Config, current_app as app
from seedboxsync.core.dao import SeedboxSync
from seedboxsync.front.babel import gettext as _
from seedboxsync.front.cache import cache
from seedboxsync.front.forms import SettingsAuthenticationForm, SettingsNasForm, SettingsPingForm, SettingsSeedboxForm, SettingsSeedboxSyncForm
from seedboxsync.front.login_manager import login_required
from seedboxsync.front.oauth2 import init_oauth2
from seedboxsync.front.views import bp_frontend as bp

msg_logger_error = "Failed to save configuration."
msg_flash_error = _("Failed to save configuration.")
msg_flash_success = _("Configuration saved successfully.")


@bp.route("/settings", methods=("GET", "POST"))
@login_required  # type: ignore[untyped-decorator]
def settings() -> str:
    """
    Render and process the general SeedboxSync settings form.

    Handles loading, displaying, and persisting application-wide
    configuration choices.

    Returns:
        str: Rendered HTML template for the main settings page.
    """
    form = SettingsSeedboxSyncForm(data=app.seedboxsync_config)

    if form.validate_on_submit():
        try:
            _save_form(form)
            flash(msg_flash_success, "success")
        except Exception as e:
            app.logger.exception(msg_logger_error, exc_info=e)
            flash(msg_flash_error, "danger")

    return render_template("settings/seedboxsync.html", form=form)


@bp.route("/settings/seedbox", methods=("GET", "POST"))
@login_required  # type: ignore[untyped-decorator]
def settings_seedbox() -> str:
    """
    Render and process the Seedbox connection settings form.

    Manages settings related to remote Seedbox access, timeouts,
    and file permission overrides.

    Returns:
        str: Rendered HTML template for the Seedbox settings page.
    """
    form = SettingsSeedboxForm(data=app.seedboxsync_config)

    if form.validate_on_submit():
        try:
            _save_form(form)
            flash(msg_flash_success, "success")
        except Exception as e:
            app.logger.exception(msg_logger_error, exc_info=e)
            flash(msg_flash_error, "danger")

    return render_template("settings/seedbox.html", form=form)


@bp.route("/settings/nas", methods=("GET", "POST"))
@login_required  # type: ignore[untyped-decorator]
def settings_nas() -> str:
    """
    Render and process the NAS storage settings form.

    Configures local destination paths and storage parameters.

    Returns:
        str: Rendered HTML template for the NAS settings page.
    """
    form = SettingsNasForm(data=app.seedboxsync_config)

    if form.validate_on_submit():
        try:
            _save_form(form)
            flash(msg_flash_success, "success")
        except Exception as e:
            app.logger.exception(msg_logger_error, exc_info=e)
            flash(msg_flash_error, "danger")

    return render_template("settings/nas.html", form=form)


@bp.route("/settings/ping", methods=("GET", "POST"))
@login_required  # type: ignore[untyped-decorator]
def settings_ping() -> str:
    """
    Render and process the ping/connectivity notification settings form.

    Configures heartbeat signals and external notification endpoints.

    Returns:
        str: Rendered HTML template for the Ping settings page.
    """
    form = SettingsPingForm(data=app.seedboxsync_config)

    if form.validate_on_submit():
        try:
            _save_form(form)
            flash(msg_flash_success, "success")
        except Exception as e:
            app.logger.exception(msg_logger_error, exc_info=e)
            flash(msg_flash_error, "danger")

    return render_template("settings/ping.html", form=form)


@bp.route("/settings/authentication", methods=("GET", "POST"))
@login_required  # type: ignore[untyped-decorator]
def settings_authentication() -> str:
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
            _save_form(form)
            init_oauth2(app)
            flash(msg_flash_success, "success")
        except Exception as e:
            app.logger.exception(msg_logger_error, exc_info=e)
            flash(msg_flash_error, "danger")

    return render_template("settings/authentication.html", form=form)


# -------------------------
# Helpers
# -------------------------
def _save_form(form: FlaskForm) -> None:
    """
    Persist submitted settings form values into runtime memory and database.

    Extracts field values, formats boolean toggles, applies specific
    feature-flag overrides, updates the active Flask app configuration mapping,
    and updates database records in a batch query.

    Args:
        form (FlaskForm): Validated WTForms form instance containing new config values.
    """
    seedbox_timeout_enabled = request.form.get("seedbox_timeout_enabled", "0") == "1"
    seedbox_chmod_enabled = request.form.get("seedbox_chmod_enabled", "0") == "1"
    config_to_db: list[dict[str, str]] = []
    config_to_update: dict[str, Any] = {}

    # Load data from form
    for field in form:
        key = field.name

        if key in {"csrf_token", "submit"}:
            continue

        if key.endswith(("_enabled", "_disabled")):  # Boolean
            value = bool(int(field.data))
            db_value = int(field.data)
        else:
            value = field.data
            db_value = field.data

        app.logger.debug(f"Updated config[{Config.CONFIG_NAMESPACE}{key.upper()}] = {value}")
        config_to_update[f"{Config.CONFIG_NAMESPACE}{key.upper()}"] = value
        config_to_db.append({"key": f"{Config.DB_CONFIG_PREFIX}{key}", "value": str(db_value)})

    # Override seedbox_timeout & seedbox_chmod
    if "seedbox_timeout" in form and not seedbox_timeout_enabled:
        app.logger.debug(f"Override config[{Config.CONFIG_NAMESPACE}SEEDBOX_TIMEOUT] = False")
        config_to_update[f"{Config.CONFIG_NAMESPACE}SEEDBOX_TIMEOUT"] = False
        config_to_db.append({"key": f"{Config.DB_CONFIG_PREFIX}seedbox_timeout", "value": "0"})
        form["seedbox_timeout"].data = "0"
    if "seedbox_chmod" in form and not seedbox_chmod_enabled:
        app.logger.debug(f"Override config[{Config.CONFIG_NAMESPACE}SEEDBOX_CHMOD] = False")
        config_to_update[f"{Config.CONFIG_NAMESPACE}SEEDBOX_CHMOD"] = False
        config_to_db.append({"key": f"{Config.DB_CONFIG_PREFIX}seedbox_chmod", "value": "0"})
        form["seedbox_chmod"].data = "0"

    # Synchronize core Flask-Login & Flask-Wtf configuration flags
    login_disabled_key = f"{Config.CONFIG_NAMESPACE}LOGIN_DISABLED"
    if login_disabled_key in config_to_update:
        app.config["LOGIN_DISABLED"] = config_to_update[login_disabled_key]
    wtf_csrt_disabled_key = f"{Config.CONFIG_NAMESPACE}WTF_CSRF_ENABLED"
    if wtf_csrt_disabled_key in config_to_update:
        app.config["WTF_CSRF_ENABLED"] = config_to_update[wtf_csrt_disabled_key]

    # Update config in Flask app
    app.config.from_mapping(config_to_update)

    # Save in database
    SeedboxSync.replace_many(config_to_db).execute()  # type: ignore[no-untyped-call]

    # Clear cache to ensure new settings take effect
    cache.clear()
