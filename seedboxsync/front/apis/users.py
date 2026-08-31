#
# Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
"""SeedboxSync api uploads view."""

from typing import Any
from flask_login import current_user
from flask_restx import Namespace, fields
from seedboxsync.front.apis import Resource
from seedboxsync.front.login_manager import login_required

api = Namespace("users", description="Operations related to users")


# ==========================
# Models
# ==========================
user_model = api.model(
    "User",
    {
        "id": fields.Integer(
            required=True,
            description="Unique identifier of the user",
            example=99,
        ),
        "username": fields.String(required=True, description="User username", example="me"),
        "email": fields.String(
            required=True,
            description="User email",
            example="me@domain.ltd",
        ),
    },
)
user_list_envelope = Resource.build_envelope_model(api, "UserList", nested_model=user_model)
user_envelope = Resource.build_envelope_model(api, "User", nested_model=user_model, as_list=False)
user_message_envelope = Resource.build_envelope_model(api, "UserMessage", as_message=True)


# ==========================
# Endpoints
# ==========================
@api.route("/me")
class Me(Resource):
    """API Resource for retrieving details about the authenticated user."""

    @api.doc("list_uploads")  # type: ignore[untyped-decorator]
    @api.marshal_with(user_envelope, code=200, skip_none=True, description="List of uploaded torrents")  # type: ignore[untyped-decorator]
    @login_required  # type: ignore[untyped-decorator]
    def get(self) -> dict[str, Any]:
        """
        Get current authenticated user profile information.

        Returns:
            dict[str, int | str]: A dictionary containing the current user's ID and username.
        """
        user = {
            "id": current_user.id,
            "username": current_user.username,
            "email": current_user.email,
        }

        return self.build_envelope(user, type="User")
