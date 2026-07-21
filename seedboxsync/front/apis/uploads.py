#
# Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
"""SeedboxSync api uploads view."""

from typing import Any
from flask_restx import Namespace, fields, reqparse
from seedboxsync.core.dao import Torrent
from seedboxsync.front.apis import Resource

api = Namespace("uploads", description="Operations related to uploaded torrents management")


# ==========================
# Models
# ==========================
upload_model = api.model(
    "Upload",
    {
        "id": fields.Integer(
            required=True,
            description="Unique identifier of the uploaded torrent",
            example=99,
        ),
        "name": fields.String(required=True, description="Torrent file name", example="Justo.torrent"),
        "announce": fields.String(
            required=False,
            description="Announce URL or tracker information from the torrent file",
            example="https://serversecret.com/anounce",
        ),
        "sent": fields.DateTime(
            dt_format="iso8601",
            required=True,
            description="Timestamp when the torrent was uploaded",
        ),
    },
)
upload_list_envelope = Resource.build_envelope_model(api, "UploadList", nested_model=upload_model)
upload_envelope = Resource.build_envelope_model(api, "Upload", nested_model=upload_model, as_list=False)
upload_message_envelope = Resource.build_envelope_model(api, "UploadMessage", as_message=True)


# ==========================
# Request parser
# ==========================
parser = reqparse.RequestParser()
parser.add_argument(
    "offset",
    type=int,
    default=0,
    location="args",
    help="Number of items to skip before starting to collect the result set (default: 0)",
)
parser.add_argument(
    "limit",
    type=int,
    default=50,
    location="args",
    help="Maximum number of items to return (min=5, max=1000)",
)
parser.add_argument("search", type=str, required=False, help="Optional search string to filter items")


# ==========================
# Endpoints
# ==========================
@api.route("")
class UploadsList(Resource):
    """
    Endpoint to manage uploaded torrents.

    Provides a list of uploaded torrents with optional limit on the number of items returned.
    """

    @api.doc("list_uploads")  # type: ignore[untyped-decorator]
    @api.expect(parser)  # type: ignore[untyped-decorator]
    @api.marshal_with(upload_list_envelope, code=200, description="List of uploaded torrents")  # type: ignore[untyped-decorator]
    def get(self) -> dict[str, Any]:
        """
        Retrieve the most recent uploaded torrents.

        Query Parameters:
        - offset: Number of items to skip before starting to collect the result set (default: 0)
        - limit: Maximum number of downloads to return (default=50)
        - search: Optional search string to filter items
        """
        args = parser.parse_args()
        offset = args.get("offset")
        limit = self.set_limit(args.get("limit"))
        search = args.get("search")

        count = Torrent.select()
        select = Torrent.select(Torrent.id, Torrent.name, Torrent.sent).limit(limit).offset(offset).order_by(Torrent.sent.desc())

        if search:
            count = count.where(Torrent.name.contains(search))
            select = select.where(Torrent.name.contains(search))

        return self.build_envelope(list(select.dicts()), data_total=count.count(), type="Upload")


@api.route("/<int:id>")
@api.response(404, "Upload not found")
@api.param("id", "The upload identifier")
class Uploads(Resource):
    """
    Endpoint for managing upload.

    Provides upload operations.
    """

    @api.doc("get_upload")  # type: ignore[untyped-decorator]
    @api.marshal_with(upload_envelope, code=200, description="Upload element")  # type: ignore[untyped-decorator]
    def get(self, id: int) -> dict[str, Any]:  # noqa: A002
        """
        Retrieve an uploaded torrent.

        Args:
            id (int): Uploaded torrent identifier.

        Returns:
            dict[str, Any]: API response envelope containing the upload.
        """
        try:
            select = Torrent.select(Torrent.id, Torrent.name, Torrent.sent).where(Torrent.id == id).dicts().get()
        except Torrent.DoesNotExist:  # type: ignore[attr-defined]
            api.abort(404, f"Upload {id} doesn't exist")

        return self.build_envelope(select, type="Upload")

    @api.doc("delete_upload")  # type: ignore[untyped-decorator]
    @api.marshal_with(upload_message_envelope, code=200, description="Delete upload element")  # type: ignore[untyped-decorator]
    def delete(self, id: int) -> dict[str, Any]:  # noqa: A002
        """
        Delete an uploaded torrent.

        Args:
            id (int): Uploaded torrent identifier.

        Returns:
            dict[str, Any]: API response envelope containing a status message.
        """
        count = Torrent.delete().where(Torrent.id == id).execute()
        if count == 0:
            api.abort(404, f"Upload {id} doesn't exist")

        return self.build_envelope(None, type="Upload", message=f"Upload {id} deleted.")
