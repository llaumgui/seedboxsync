#
# Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
"""SeedboxSync front i18n module."""

from flask import request
from flask_babel import Babel
from seedboxsync.core import Config, current_app as app

babel = Babel()
ALLOWED_LANGUAGES = ["fr", "en"]


def get_locale() -> str | None:
    """
    Get locale from browser.

    Returns:
        str: The local.
    """
    locale = app.config.get(Config.CONFIG_NAMESPACE + "WEBUI_LANGUAGE", "auto")
    if locale != "auto":
        return str(locale)
    return request.accept_languages.best_match(ALLOWED_LANGUAGES)
