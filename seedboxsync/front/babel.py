# -*- coding: utf-8 -*-
#
# Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
from flask import request
from flask_babel import Babel

babel = Babel()


def get_locale() -> str | None:
    """
    Get locale from browser.

    Returns:
        str: The local.
    """
    return request.accept_languages.best_match(["fr", "en"])
