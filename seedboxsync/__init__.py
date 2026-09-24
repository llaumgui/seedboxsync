#
# Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
"""The SeedboxSync main package."""

from collections.abc import Callable, Iterable
from datetime import datetime
from pathlib import Path
from typing import Any
from flask import Response, flash, g, request, send_from_directory, session
from flask_babel import format_datetime, get_locale as get_babel_locale
from humanize import i18n as humanize_i18n
from libgravatar import Gravatar
from slugify import slugify
from werkzeug.middleware.proxy_fix import ProxyFix
from seedboxsync.__version__ import (
    __api_path_version__ as api_path_version,
    __api_version__ as api_version,
    __version__ as version,
)
from seedboxsync.core import Config, Database, Flask, logger
from seedboxsync.front.apis import register_api_blueprint
from seedboxsync.front.apis.core import error as error_api
from seedboxsync.front.babel import babel, get_locale
from seedboxsync.front.cache import cache
from seedboxsync.front.login_manager import login_manager
from seedboxsync.front.oauth2 import init_oauth2
from seedboxsync.front.views import bp_auth, bp_frontend, bp_settings, error as error_front

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


def __gravatar(email: str) -> str:
    """
    Generate the Gravatar image URL for a given email address.

    Args:
        email (str): The target user's email address.

    Returns:
        str: The fully qualified URL pointing to the user's Gravatar profile image.
    """
    return str(Gravatar(email).get_image())


def __get_toasted_messages(with_categories: bool = False, category_filter: Iterable[str] = ()) -> list[str] | list[tuple[str, str]]:
    """
    Retrieve and clear pending toast notifications from the Flask session.

    Acts as a specialized alternative to Flask's ``get_flashed_messages()`` specifically
    tailored for toast notifications, pulling messages from ``g`` or removing them
    from the user session[cite: 1, 5].

    Args:
        with_categories (bool, optional): If True, returns tuples of ``(category, message)``.
            If False, returns only the message strings. Defaults to False.
        category_filter (Iterable[str], optional): An iterable of category names used to
            filter the returned toasts[cite: 1]. Defaults to ().

    Returns:
        list[str] | list[tuple[str, str]]: A list of toast message strings if ``with_categories``
            is False, or a list of ``(category, message)`` tuples if ``with_categories`` is True.
    """
    toasts = getattr(g, "_toasts", None)
    if toasts is None:
        toasts = g._toasts = session.pop("_toasts", [])
    if category_filter:
        toasts = [toast for toast in toasts if toast[0] in category_filter]

    if with_categories:
        return toasts

    return [toast[1] for toast in toasts]


def create_app(injected_config: dict[str, str | bool] | None = None) -> Flask:
    """
    Create and configure the SeedboxSync Flask application.

    Args:
        injected_config (dict[str, str] | None): Optional configuration overrides
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

    # ══════════════════════════════════════════════════════════════════════════════
    # ⚙️  INIT
    # ══════════════════════════════════════════════════════════════════════════════
    # Configure logger for Flask and Click
    logger.configure_logger(app.logger)

    # Load test config
    if injected_config is not None:
        app.config.from_mapping(injected_config)  # load the test config if passed in

    # Initialize the database
    database = Database(app)
    app.extensions["database"] = database

    # Load config
    Config(app)

    # Initialize Babel
    app.config["BABEL_TRANSLATION_DIRECTORIES"] = "front/translations"
    babel.init_app(app, locale_selector=get_locale)

    # Initialize the cache
    cache.init_app(app)

    # Initialize the login manager and OAuth
    login_manager.init_app(app)
    init_oauth2(app)

    # Register jinja filter
    app.jinja_env.filters["slugify"] = slugify

    # Register blueprint and error handler
    app.register_blueprint(bp_auth)
    app.register_blueprint(bp_frontend)
    app.register_blueprint(bp_settings)
    register_api_blueprint(app)
    app.register_error_handler(Exception, __handle_http_exception)  # type: ignore[arg-type]

    # Set up ProxyFix middleware to handle reverse proxy headers
    app.wsgi_app = ProxyFix(  # type: ignore[method-assign]
        app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1
    )

    # ══════════════════════════════════════════════════════════════════════════════
    # ⚙️  FUNCTIONS
    # ══════════════════════════════════════════════════════════════════════════════
    # Routes
    @app.route("/favicon.ico")
    def favicon() -> Response:  # pyright: ignore [reportUnusedFunction]
        """Serve the favicon from the static directory."""
        return send_from_directory(Path(app.root_path, "front/static"), "favicon.png", mimetype="image/png")

    # Before Request
    @app.before_request
    def init_once() -> None:  # pyright: ignore [reportUnusedFunction]
        """Initialize humanize for each request."""
        humanize_i18n.activate(get_locale())

    @app.before_request
    def check_init_error() -> None:  # pyright: ignore [reportUnusedFunction]
        """Display initialization errors as flash messages if any."""
        init_error = app.config.pop("INIT_ERROR", None)
        if init_error:
            flash(init_error, "danger")

    # Context processor
    @app.context_processor
    def inject_formatters() -> dict[str, Callable[[datetime], str]]:  # pyright: ignore [reportUnusedFunction]
        """Inject custom formatters into the template context."""
        return {"format_datetime": format_datetime}

    @app.context_processor
    def inject_globals() -> dict[str, Any]:  # pyright: ignore [reportUnusedFunction]
        """Inject global variables into the template context."""
        locale = str(get_babel_locale() or app.config.get("BABEL_DEFAULT_LOCALE", "en_US"))
        lang = locale.split("_")[0].split("-")[0]
        theme = app.config.get(Config.CONFIG_NAMESPACE + "WEBUI_THEME", "auto")

        return {
            "api_version": api_version,
            "lang": lang,
            "locale": locale,
            "seedboxsync_config": app.seedboxsync_config,
            "theme": theme,
            "version": version,
        }

    # Template global
    @app.template_global()
    def gravatar(email: str) -> str:  # pyright: ignore [reportUnusedFunction]
        """Return the Gravatar image URL for an email address."""
        return __gravatar(email)

    @app.template_global()
    def get_toasted_messages(with_categories: bool = False, category_filter: Iterable[str] = ()) -> list[str] | list[tuple[str, str]]:
        """Like a flash but for toast."""
        return __get_toasted_messages(with_categories, category_filter)

    return app
