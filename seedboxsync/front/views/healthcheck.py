#
# Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
"""SeedboxSync Flask vierw for healthcheck."""
from flask import Response, jsonify
from seedboxsync.front.views import bp


@bp.route("/healthcheck")
def healthcheck() -> tuple[Response, int]:
    """Healthcheck view."""
    return jsonify({"status": "ok"}), 200
