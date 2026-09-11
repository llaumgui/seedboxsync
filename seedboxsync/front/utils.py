#
# Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
"""SeedboxSync utils and helpers for frontend."""

from typing import Any
from urllib.parse import urlsplit
from flask import request
from flask_wtf import FlaskForm
from seedboxsync.core import Config, current_app as app
from seedboxsync.core.database.models import SeedboxSync
from seedboxsync.front.cache import cache


def is_safe_redirect_url(target: str) -> bool:
    """
    Check whether a target URL is safe for local redirection.

    Only absolute local paths are allowed. External URLs, scheme-relative
    URLs, and paths containing backslashes are rejected.

    Args:
        target: The target URL string to validate.

    Returns:
        True if the target is a safe local absolute path, False otherwise.
    """
    if not target.startswith("/"):
        return False

    # Reject scheme-relative and browser-specific absolute URL forms.
    if target.startswith("//") or "\\" in target:
        return False

    try:
        url = urlsplit(target)
    except ValueError:
        return False

    return not url.scheme and not url.netloc


def save_settings_form(form: FlaskForm) -> None:
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
