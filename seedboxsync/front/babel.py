#
# Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
"""SeedboxSync front i18n module."""

from typing import cast
from flask import request
from flask_babel import Babel, lazy_gettext
from seedboxsync.core import Config, current_app as app

babel = Babel()
ALLOWED_LANGUAGES = ["fr", "en"]


def gettext(message: str) -> str:
    """
    Return a lazily translated string with a type compatible with WTForms.

    The cast is required because Flask-Babel returns a LazyString while
    WTForms type annotations expect a str.
    """
    return cast(str, lazy_gettext(message))


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
