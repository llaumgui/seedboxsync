#
# Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
"""SeedboxSync Flask view for healthcheck."""

from flask import Response, jsonify
from seedboxsync.front.views import bp_frontend as bp


@bp.route("/healthcheck")
def healthcheck() -> tuple[Response, int]:
    """
    Perform a basic HTTP health check.

    Returns:
        tuple[Response, int]: JSON response with health status ("ok") and HTTP status code 200.
    """
    return jsonify({"status": "ok"}), 200
