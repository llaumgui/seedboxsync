# -*- coding: utf-8 -*-
#
# Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
import os
import humanize
from seedboxsync.core import Flask
from flask import Response, request, send_from_directory
from flask_babel import format_datetime, get_locale as get_babel_locale
from datetime import datetime
from typing import Callable
from seedboxsync.core import Config, Database, logger
from seedboxsync.front.views import bp as bp_frontend, error as error_front
from seedboxsync.front.apis import bp as bp_api, error as error_api
from seedboxsync.front.babel import babel, get_locale
from seedboxsync.front.cache import cache
from seedboxsync.__version__ import (
    __version__ as version,
    __api_version__ as api_version,
    __api_path_version__ as api_path_version,
)

__version__ = version


def __handle_http_exception(
    e: Exception,
) -> tuple[Response, int | None] | tuple[str, int | None]:
    """
    Global 404 handler.

    Args:
        e (Exception): Exception raised while processing the request.

    Returns:
        tuple[Response, int | None] | tuple[str, int | None]: JSON for /api routes, else return frontend template.
    """
    if request.path.startswith(f"/api/{api_path_version}") or request.blueprint == "api":
        return error_api.error(e)
    return error_front.error(e)


def create_app(test_config: dict[str, str] | None = None) -> Flask:
    """
    Create and configure the SeedboxSync Flask application.

    Args:
        test_config (dict[str, str] | None): Optional configuration overrides
            used by tests.

    Returns:
        Flask: Configured application instance.
    """
    # Create and configure the app
    app = Flask(
        __name__,
        template_folder="front/templates",
        static_folder="front/static",
        instance_relative_config=True,
    )

    # Configure logger for Flask and Click
    logger.configure_logger(app.logger)

    # Load test config
    if test_config is not None:
        app.config.from_mapping(test_config)  # load the test config if passed in

    # Initialize the database
    Database(app)

    # Load config
    Config(app)

    # Initialize Babel
    app.config["BABEL_TRANSLATION_DIRECTORIES"] = "front/translations"
    babel.init_app(app, locale_selector=get_locale)

    # Initialize humanize for each request
    @app.before_request
    def init_once() -> None:
        humanize.i18n.activate(get_locale())

    # Inject Jinja function / variables
    @app.context_processor
    def inject_formatters() -> dict[str, Callable[[datetime], str]]:
        return dict(format_datetime=format_datetime)

    @app.context_processor
    def inject_globals() -> dict[str, str]:
        locale = get_babel_locale() or app.config.get("BABEL_DEFAULT_LOCALE", "en")
        return {
            "version": version,
            "api_version": api_version,
            "locale": str(locale).replace("_", "-"),
        }

    # Initialize the cache
    cache.init_app(app)

    # Register blueprint and error handler
    app.register_blueprint(bp_frontend)
    app.register_blueprint(bp_api)
    app.register_error_handler(Exception, __handle_http_exception)  # type: ignore[arg-type]

    # Serve the favicon from the static directory
    @app.route("/favicon.ico")
    def favicon() -> Response:
        return send_from_directory(os.path.join(app.root_path, "static"), "favicon.png", mimetype="image/png")

    return app
