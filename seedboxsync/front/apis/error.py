# -*- coding: utf-8 -*-
#
# Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
import uuid
from flask import jsonify, Response
from flask_babel import gettext
from werkzeug.exceptions import BadRequest, HTTPException, NotFound
from datetime import datetime
from typing import Any
from seedboxsync.front.apis import api


@api.errorhandler(BadRequest)  # type: ignore[untyped-decorator]
@api.errorhandler(NotFound)  # type: ignore[untyped-decorator]
def api_errorhandler(error: BadRequest | NotFound) -> tuple[dict[str, Any], int]:
    """
    API error handler.
    :param e: Exception
    :return: Rendered error template with status code
    """
    status_code = error.code if isinstance(error, HTTPException) else 500

    error.data = {  # type: ignore[union-attr]
        "type": "about:blank",
        "success": False,
        "status": status_code,
        "title": error.data.get("message", ""),  # type: ignore[union-attr]
        **({"message": error.data["errors"]} if "errors" in error.data else {}),  # type: ignore[union-attr]
        "timestamp": datetime.now().astimezone().isoformat(),
        "traceId": str(uuid.uuid4()),
    }

    return {}, status_code


def error(exc: Exception) -> tuple[Response, int | None]:
    """
    Global error handler.
    :param e: Exception
    :return: Rendered error template with status code
    """
    status_code = exc.code if isinstance(exc, HTTPException) else 500
    title = exc.name if isinstance(exc, HTTPException) else gettext("Internal Server Error")
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
