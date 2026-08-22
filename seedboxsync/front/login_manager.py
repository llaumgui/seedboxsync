#
# Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
"""SeedboxSync login manager module using Flask-Login."""

from flask_babel import gettext
from flask_login import LoginManager, login_required as flask_login_required
from seedboxsync.core.dao import User

# Setup Flask-Login
login_manager = LoginManager()
login_manager.login_view = "frontend.login"  # pyright: ignore[reportAttributeAccessIssue]
login_manager.login_message = gettext("Please log in to access this page.")
login_manager.login_message_category = "info"


@login_manager.user_loader  # type: ignore[untyped-decorator]
def load_user(user_id: str) -> "User | None":
    """Load a user by their ID."""
    return User.get(user_id)


login_required = flask_login_required
