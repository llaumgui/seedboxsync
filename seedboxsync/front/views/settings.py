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
from seedboxsync.front.forms import SettingsNasForm, SettingsPingForm, SettingsSeedboxForm, SettingsSeedboxSyncForm
from seedboxsync.front.login_manager import login_required
from seedboxsync.front.utils import init_flash
from seedboxsync.front.views import bp

msg_logger_error = "Failed to save config"
msg_flash_error = _("Failed to save config")


@bp.route("/settings", methods=("GET", "POST"))
@login_required  # type: ignore[untyped-decorator]
def settings() -> str:
    """Manage settings: load configuration, display form, persist changes."""
    init_flash()
    saved = False
    form = SettingsSeedboxSyncForm(data=app.seedboxsync_config)

    if form.validate_on_submit():
        try:
            _save_form(form)
            saved = True
        except Exception as e:
            app.logger.exception(msg_logger_error, exc_info=e)
            flash(msg_flash_error, "error")

    return render_template("settings/seedboxsync.html", form=form, saved=saved)


@bp.route("/settings/seedbox", methods=("GET", "POST"))
@login_required  # type: ignore[untyped-decorator]
def settings_seedbox() -> str:
    """Manage settings: load configuration, display form, persist changes."""
    init_flash()
    saved = False
    form = SettingsSeedboxForm(data=app.seedboxsync_config)

    if form.validate_on_submit():
        try:
            _save_form(form)
            saved = True
        except Exception as e:
            app.logger.exception(msg_logger_error, exc_info=e)
            flash(msg_flash_error, "error")

    return render_template("settings/seedbox.html", form=form, saved=saved)


@bp.route("/settings/nas", methods=("GET", "POST"))
@login_required  # type: ignore[untyped-decorator]
def settings_nas() -> str:
    """Manage settings: load configuration, display form, persist changes."""
    init_flash()
    saved = False
    form = SettingsNasForm(data=app.seedboxsync_config)

    if form.validate_on_submit():
        try:
            _save_form(form)
            saved = True
        except Exception as e:
            app.logger.exception(msg_logger_error, exc_info=e)
            flash(msg_flash_error, "error")

    return render_template("settings/nas.html", form=form, saved=saved)


@bp.route("/settings/ping", methods=("GET", "POST"))
@login_required  # type: ignore[untyped-decorator]
def settings_ping() -> str:
    """Manage settings: load configuration, display form, persist changes."""
    init_flash()
    saved = False
    form = SettingsPingForm(data=app.seedboxsync_config)

    if form.validate_on_submit():
        try:
            _save_form(form)
            saved = True
        except Exception as e:
            app.logger.exception(msg_logger_error, exc_info=e)
            flash(msg_flash_error, "error")

    return render_template("settings/ping.html", form=form, saved=saved)


# -------------------------
# Helpers
# -------------------------
def _save_form(form: FlaskForm) -> None:
    """Save form data to the configuration file."""
    seedbox_timeout_enabled = request.form.get("seedbox_timeout_enabled", "0") == "1"
    seedbox_chmod_enabled = request.form.get("seedbox_chmod_enabled", "0") == "1"
    config_to_db: list[dict[str, str]] = []
    config_to_update: dict[str, Any] = {}

    # Load data from form
    for field in form:
        key = field.name

        if key in {"csrf_token", "submit"}:
            continue

        if key.endswith("_enabled"):  # Boolean
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

    # Update config in Flask app
    app.config.from_mapping(config_to_update)

    # Save in database
    SeedboxSync.replace_many(config_to_db).execute()  # type: ignore[no-untyped-call]
