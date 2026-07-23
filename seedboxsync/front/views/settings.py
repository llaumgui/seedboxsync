#
# Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
"""SeedboxSync Flask vierw for settings."""

from collections.abc import Iterable
from typing import Any
from flask import flash, render_template, request
from flask.wrappers import Request
from flask_babel import gettext
from seedboxsync.core import Config, current_app as app
from seedboxsync.core.dao import SeedboxSync
from seedboxsync.front.babel import ALLOWED_LANGUAGES
from seedboxsync.front.utils import init_flash
from seedboxsync.front.views import bp


@bp.route("/settings", methods=("GET", "POST"))
def settings() -> str:
    """Manage settings: load configuration, display form, persist changes."""
    init_flash()
    saved = False
    languages_list = ALLOWED_LANGUAGES

    form = _build_form()

    if request.method == "POST":
        missing = [f for f in _required_form_fields() if not request.form.get(f)]
        if missing:
            flash(
                gettext("Missing required fields: %(missing)s", missing=", ".join(missing)),
                "error",
            )
        else:
            try:
                _save_form(request)
                form = _build_form()  # reload cleaned values
                saved = True
            except Exception as e:
                app.logger.exception("Failed to save config", exc_info=e)
                flash(gettext("Failed to save configuration."), "error")

    return render_template("settings.html", form=form, saved=saved, languages_list=languages_list)


# -------------------------
# Helpers
# -------------------------
def _required_form_fields() -> Iterable[str]:
    """
    List of all requitred fields.

    Returns:
        True if the value represents an enabled/true state, otherwise False.
    """
    return [
        "seedbox_host",
        "seedbox_port",
        "seedbox_login",
        "seedbox_password",
        "seedbox_protocol",
        "seedbox_tmp_path",
        "seedbox_watch_path",
        "seedbox_finished_path",
        "seedbox_part_suffix",
    ]


def _build_form() -> dict[str, Any]:
    """
    Build form fields.

    Returns:
        Dictionnary of fields.
    """
    fields = {key: ((1 if value else 0) if key.endswith("_enabled") else (0 if value is False else value)) for key, value in app.seedboxsync_config.items()}
    fields.setdefault(
        "seedbox_timeout_enabled",
        "1" if fields.get("seedbox_timeout", "0") not in ["", "0", False] else "0",
    )
    fields.setdefault(
        "seedbox_chmod_enabled",
        "1" if fields.get("seedbox_chmod", "0") not in ["", "0", False] else "0",
    )

    return fields


def _as_bool(value: str | None) -> bool:
    """
    Convert a form value to a boolean.

    Args:
        value: The raw form value.

    Returns:
        True if the value represents an enabled/true state, otherwise False.
    """
    if value is None:
        return False

    return value.strip().lower() in {"1"}


def _save_form(req: Request) -> None:
    """Save form data to the configuration file."""
    seedbox_timeout_enabled = req.form.get("seedbox_timeout_enabled", "0") == "1"
    seedbox_chmod_enabled = req.form.get("seedbox_chmod_enabled", "0") == "1"
    fields = app.seedboxsync_config
    config_to_db: list[dict[str, str]] = []
    config_to_update: dict[str, Any] = {}

    for key in fields:
        value: str | bool
        if key in req.form:
            value = str(req.form[key] or "").strip()
            db_value = value
            if key.endswith("_enabled"):
                value = bool(int(value))
        elif key not in req.form and key.endswith("_enabled"):
            value = False
            db_value = "0"

        app.logger.debug(f"Updated config[{Config.CONFIG_NAMESPACE}{key.upper()}] = {value}")
        config_to_update[f"{Config.CONFIG_NAMESPACE}{key.upper()}"] = value
        config_to_db.append(
            {
                "key": f"{Config.DB_CONFIG_PREFIX}{key}",
                "value": db_value,
            }
        )

    if not seedbox_timeout_enabled:
        app.logger.debug(f"Updated config[{Config.CONFIG_NAMESPACE}SEEDBOX_TIMEOUT] = False")
        config_to_update[f"{Config.CONFIG_NAMESPACE}SEEDBOX_TIMEOUT"] = False
        config_to_db.append(
            {
                "key": f"{Config.DB_CONFIG_PREFIX}seedbox_timeout",
                "value": "0",
            }
        )

    if not seedbox_chmod_enabled:
        app.logger.debug(f"Updated config[{Config.CONFIG_NAMESPACE}SEEDBOX_CHMOD] = False")
        config_to_update[f"{Config.CONFIG_NAMESPACE}SEEDBOX_CHMOD"] = False
        config_to_db.append(
            {
                "key": f"{Config.DB_CONFIG_PREFIX}seedbox_chmod",
                "value": "0",
            }
        )

    # Update config in Flask app
    app.config.from_mapping(config_to_update)

    # Save in database
    SeedboxSync.replace_many(config_to_db).execute()  # type: ignore[no-untyped-call]
