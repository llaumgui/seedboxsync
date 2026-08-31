#
# Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
"""SeedboxSync api error module."""

from datetime import datetime
from typing import Any
import uuid
from flask import Response, jsonify
from werkzeug.exceptions import BadRequest, HTTPException, NotFound, Unauthorized
from seedboxsync.front.apis import api
from seedboxsync.front.babel import gettext as _


@api.errorhandler(BadRequest)  # type: ignore[untyped-decorator]
@api.errorhandler(NotFound)  # type: ignore[untyped-decorator]
@api.errorhandler(Unauthorized)  # type: ignore[untyped-decorator]
def api_errorhandler(error: BadRequest | NotFound | Unauthorized) -> tuple[dict[str, Any], int]:
    """
    Handle validation and not-found API errors.

    Args:
        error (BadRequest | NotFound | Unauthorized): HTTP exception to serialize.

    Returns:
        tuple[dict[str, Any], int]: Empty response body and HTTP status code.
    """
    status_code = error.code or 500

    # Get Flask-RESTX error data or build it from the HTTP exception
    data = getattr(
        error,
        "data",
        {
            "message": error.name,
            "errors": error.description,
        },
    )

    error.data = {  # type: ignore[union-attr]
        "type": "about:blank",
        "success": False,
        "status": status_code,
        "title": data.get("message", ""),
        **({"message": data["errors"]} if "errors" in data else {}),
        "timestamp": datetime.now().astimezone().isoformat(),
        "traceId": str(uuid.uuid4()),
    }

    return {}, status_code


def error(exc: Exception) -> tuple[Response, int | None]:
    """
    Serialize an exception as a JSON API response.

    Args:
        exc (Exception): Exception raised while processing the request.

    Returns:
        tuple[Response, int | None]: JSON response and HTTP status code.
    """
    status_code = exc.code if isinstance(exc, HTTPException) else 500
    title = exc.name if isinstance(exc, HTTPException) else _("Internal Server Error")
    message = exc.description if isinstance(exc, HTTPException) else str(exc)

    return (
        jsonify(
            {
                "type": "about:blank",
                "success": False,
                "status": status_code,
                "title": title,
                "message": message,
                "timestamp": datetime.now().astimezone().isoformat(),
                "traceId": str(uuid.uuid4()),
            }
        ),
        status_code,
    )
