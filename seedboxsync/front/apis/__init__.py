#
# Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
"""SeedboxSync api package."""

from flask import Blueprint
from flask_restx import Api
from seedboxsync.__version__ import (
    __api_path_version__ as api_path_version,
    __api_version__ as api_version,
)
from seedboxsync.core import Flask

from seedboxsync.front.apis.core.resources import parser_period, DateTimeOrZero, Resource  # isort: skip
from seedboxsync.front.apis.downloads import api as nsDownloads
from seedboxsync.front.apis.tasks import api as nsTasks
from seedboxsync.front.apis.taskstatus import api as nsTaskStatus
from seedboxsync.front.apis.uploads import api as nsUploads
from seedboxsync.front.apis.users import api as nsUsers

bp = Blueprint("api", __name__, url_prefix=f"/api/{api_path_version}")

api = Api(
    title="SeedboxSync API",
    version=api_version,
    description="REST API providing access to the SeedboxSync database and its resources.",
    validate=True,
)

# Add namespaces
api.add_namespace(nsDownloads)
api.add_namespace(nsUploads)
api.add_namespace(nsTasks)
api.add_namespace(nsTaskStatus)
api.add_namespace(nsUsers)

__all__ = ["DateTimeOrZero", "Resource", "parser_period"]


def register_api_blueprint(app: Flask) -> None:
    """
    Configure OpenAPI/Swagger security definitions for Flask-RESTX and register Blueprint.

    Registers HTTP Basic Authentication schemes in the Swagger UI
    documentation unless authentication is globally disabled.

    Args:
        app (Flask): The Flask application instance containing configuration flags.
    """
    if not app.config.get("LOGIN_DISABLED", False):
        api.authorizations = {
            "basicAuth": {
                "type": "basic",
                "description": "Basic authentication with username and password",
            },
            "apiKey": {
                "type": "apiKey",
                "in": "header",
                "name": "X-API-Key",
                "description": "API key authentication (e.g. 'X-API-Key: sbx_...')",
            },
        }
        api.security = ["basicAuth", "apiKey"]

    if api.blueprint is None:
        api.init_app(bp)
    app.register_blueprint(bp)
