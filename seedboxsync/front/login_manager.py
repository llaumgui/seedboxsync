#
# Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
"""SeedboxSync login manager module using Flask-Login."""

from collections.abc import Callable
from functools import wraps
from typing import Any
from flask import Request, Response, abort, current_app, redirect, request, session, url_for
from flask_login import LoginManager, current_user, login_required as flask_login_required
from seedboxsync.core.database.models import ApiKey, User
from seedboxsync.front.babel import gettext as _

# Setup Flask-Login
login_manager = LoginManager()
login_manager.login_view = "auth.login"  # pyright: ignore[reportAttributeAccessIssue]
login_manager.login_message = _("Please log in to access this page.")
login_manager.login_message_category = "info"


def _authenticate_by_api_key(request: Request) -> User | None:
    """
    Attempt to authenticate a user using an API Key from request headers.

    Checks both the custom 'X-API-Key' header and the standard 'Authorization'
    header formatted as a Bearer token.

    Args:
        request (Request): Flask request object containing incoming headers.

    Returns:
        User | None: Authenticated User instance if valid key is provided,
            otherwise None.
    """
    headers = getattr(request, "headers", None)

    # 1. Direct X-API-Key header
    if headers is not None:
        api_key_header = headers.get("X-API-Key")
        if api_key_header:
            return ApiKey.authenticate(api_key_header)

    # 2. Authorization: Bearer token
    auth = getattr(request, "authorization", None)
    if auth and auth.type == "bearer" and getattr(auth, "token", None):
        return ApiKey.authenticate(auth.token)

    return None


@login_manager.user_loader  # type: ignore[untyped-decorator]
def load_user(user_id: str) -> "User | None":
    """
    Retrieve and load a user instance by primary key for session management.

    Callback used by Flask-Login to reload the user object from the user ID
    stored in the session.

    Args:
        user_id (str): Unique database identifier of the user as a string.

    Returns:
        User | None: The matching User instance if found, or None if no record exists.
    """
    user = User.get_or_none(User.id == int(user_id))
    if user is None:
        session.clear()  # Clear broken session.
    return user


@login_manager.unauthorized_handler  # type: ignore[untyped-decorator]
def unauthorized() -> Any | int | Response:
    """
    Handle unauthorized access attempts across application blueprints.

    Differentiates between API and Web UI behavior: returns an HTTP 401 Unauthorized
    error for API endpoints, or redirects to the login view with the original target
    URL in the 'next' query parameter for frontend routes.

    Returns:
        Any | int | Response: HTTP 401 abort error for API routes, or a Flask HTTP
            redirect response to the login page for frontend routes.
    """
    if request.blueprint == "api":
        abort(401)

    # Default behavior for the frontend
    return redirect(url_for("auth.login", next=request.path))


@login_manager.request_loader  # type: ignore[untyped-decorator]
def load_user_from_request(request: Request) -> User | None:
    """
    Load and authenticate a user from request credentials.

    Evaluates authentication strategies in sequence:
    1. API Key via 'X-API-Key' header or 'Bearer' token.
    2. HTTP Basic Authentication credentials.

    Args:
        request (Request): Flask request object containing HTTP authorization data.

    Returns:
        User | None: Authenticated User instance or None if verification fails.
    """
    # Try API Key authentication first
    user = _authenticate_by_api_key(request)
    if user is not None:
        return user

    # Fallback to HTTP Basic authentication
    auth = getattr(request, "authorization", None)
    if auth and auth.type == "basic" and auth.username and auth.password:
        try:
            return User.authenticate(auth.username, auth.password)
        except User.DoesNotExist:  # pyright: ignore[reportAttributeAccessIssue]
            return None

    return None


def is_admin_required(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    Restrict access to authenticated administrators.

    Unauthenticated users are handled by Flask-Login's unauthorized callback.
    Authenticated users whose is_admin attribute is false receive HTTP 403.

    Args:
        func: The view function to decorate.

    Returns:
        The view function wrapped with authentication and administrator checks.
    """

    @wraps(func)
    def decorated_view(*args: Any, **kwargs: Any) -> Any:
        """
        Check access permissions and execute the protected view.

        Args:
            *args: Positional arguments forwarded to the view.
            **kwargs: Keyword arguments forwarded to the view.

        Returns:
            The view's result or the unauthorized callback's response.

        Raises:
            Forbidden: If the authenticated user is not an administrator.
        """
        # Delegate unauthenticated access to Flask-Login.
        if not current_app.config.get("LOGIN_DISABLED") and not current_user.is_authenticated:
            return login_manager.unauthorized()

        # Deny access to authenticated users without administrator privileges.
        if not current_app.config.get("LOGIN_DISABLED") and not current_user.is_admin:
            abort(403)

        # Support both synchronous and asynchronous views.
        return current_app.ensure_sync(func)(*args, **kwargs)

    return decorated_view


login_required = flask_login_required
