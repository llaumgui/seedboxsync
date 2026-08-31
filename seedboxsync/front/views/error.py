#
# Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
"""SeedboxSync Flask view for errors."""

from flask import render_template
from werkzeug.exceptions import HTTPException
from seedboxsync.front.babel import gettext as _


def error(e: Exception) -> tuple[str, int | None]:
    """
    Global error handler.

    Args:
        e (Exception): The exception.

    Returns:
        str: Rendered error template with status code.
    """
    status_code = e.code if isinstance(e, HTTPException) else 500
    title = e.name if isinstance(e, HTTPException) else _("Internal Server Error")
    detail = e.description if isinstance(e, HTTPException) else str(e)

    return render_template("error.html", title=title, detail=detail), status_code
