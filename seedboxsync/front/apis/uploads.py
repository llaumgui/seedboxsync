#
# Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
"""SeedboxSync api uploads view."""

from datetime import date
from typing import Any
from flask_restx import Namespace, fields, inputs, reqparse
from peewee import fn
from seedboxsync.core.database.models import Torrent
from seedboxsync.front.apis import Resource, parser_period
from seedboxsync.front.cache import cache
from seedboxsync.front.login_manager import login_required

api = Namespace("uploads", description="Operations related to uploaded torrents management")


# ==========================
# Models
# ==========================
upload_model = api.model(
    "Upload",
    {
        "id": fields.Integer(required=True, description="Unique identifier of the uploaded torrent", example=99),
        "name": fields.String(required=True, description="Torrent file name", example="Justo.torrent"),
        "announce": fields.String(
            required=False,
            description="Announce URL or tracker information from the torrent file",
            example="https://serversecret.com/anounce",
        ),
        "announcer": fields.String(
            required=False,
            description="Tracker announce domain of the torrent",
            example="serversecret.com",
        ),
        "source": fields.String(
            required=False,
            description="Source or provenance of the torrent file",
            example="serversecret",
        ),
        "files": fields.Integer(
            required=False,
            description="Total number of files contained in the torrent",
            example=2,
        ),
        "size": fields.Integer(
            required=False,
            description="Total size of all files in bytes",
            example=3337353289,
        ),
        "human_size": fields.String(
            required=False,
            description="Total size of all files in with related humanization",
            example="3.1 GiB",
        ),
        "private": fields.Boolean(
            required=False,
            description="Flag indicating if the torrent is private",
            example=True,
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

stats_source_model = api.model(
    "StatsSource",
    {
        "source": fields.String(
            required=True,
            description="Source of the torrent, falback based on announcer",
            example="torrenter",
        ),
        "total": fields.Integer(
            required=True,
            description="Number or size of files for this source",
            example=4989,
        ),
        "total_size": fields.Integer(
            required=True,
            description="Size of files for this source",
            example=21678643250867,
        ),
        "human_total_size": fields.String(
            required=True,
            description="Total size of files with related source",
            example="19.7 Tio",
        ),
    },
)
stats_source_envelope = Resource.build_envelope_model(api, "StatsSource", nested_model=stats_source_model)


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
parser.add_argument(
    "start_date",
    type=inputs.date_from_iso8601,
    location="args",
    help="Start date for filtering in ISO 8601 format (e.g. YYYY-MM-DD)",
)
parser.add_argument(
    "end_date",
    type=inputs.date_from_iso8601,
    location="args",
    help="End date for filtering in ISO 8601 format (e.g. YYYY-MM-DD)",
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
    @login_required  # type: ignore[untyped-decorator]
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
        limit = self.set_limit(args.get("limit", 50))
        search = args.get("search")
        start_date = args.get("start_date")
        end_date = args.get("end_date")

        count = Torrent.select()
        select = (
            Torrent.select(
                Torrent.id,
                Torrent.name,
                Torrent.announce,
                Torrent.announcer,
                Torrent.source,
                fn.coalesce(Torrent.total_files, None).alias("files"),
                fn.coalesce(Torrent.total_size, None).alias("size"),
                fn.humanize(Torrent.total_size).alias("human_size"),
                Torrent.private,
                Torrent.sent,
            )
            .limit(limit)
            .offset(offset)
            .order_by(Torrent.sent.desc())
        )

        if search:
            count = count.where(Torrent.name.contains(search))
            select = select.where(Torrent.name.contains(search))

        if start_date:
            count = count.where(Torrent.sent >= start_date)
            select = select.where(Torrent.sent >= start_date)

        if end_date:
            count = count.where(Torrent.sent <= end_date)
            select = select.where(Torrent.sent <= end_date)

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
    @api.marshal_with(upload_envelope, skip_none=True, code=200, description="Upload element")  # type: ignore[untyped-decorator]
    @login_required  # type: ignore[untyped-decorator]
    def get(self, id: int) -> dict[str, Any]:  # noqa: A002
        """
        Retrieve an uploaded torrent.

        Args:
            id (int): Uploaded torrent identifier.

        Returns:
            dict[str, Any]: API response envelope containing the upload.
        """
        select: Torrent | None = None
        try:
            select = (
                Torrent.select(
                    Torrent.id,
                    Torrent.name,
                    Torrent.announce,
                    Torrent.announcer,
                    Torrent.source,
                    fn.coalesce(Torrent.total_files, None).alias("files"),
                    fn.coalesce(Torrent.total_size, None).alias("size"),
                    fn.humanize(Torrent.total_size).alias("human_size"),
                    Torrent.private,
                    Torrent.sent,
                )
                .where(Torrent.id == id)
                .dicts()
                .get()
            )

        except Torrent.DoesNotExist:  # type: ignore[attr-defined]
            api.abort(404, f"Upload {id} doesn't exist")

        return self.build_envelope(select, type="Upload")

    @api.doc("delete_upload")  # type: ignore[untyped-decorator]
    @api.marshal_with(upload_message_envelope, code=200, description="Delete upload element")  # type: ignore[untyped-decorator]
    @login_required  # type: ignore[untyped-decorator]
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


@api.route("/stats/source")
class UploadsStatsBySource(Resource):
    """Resource endpoint to retrieve torrent source statistics."""

    @api.doc("stats_uploads_by_source")  # type: ignore[untyped-decorator]
    @api.marshal_with(stats_source_envelope, code=200, description="Upload statistics aggregated by source")  # type: ignore[untyped-decorator]
    @api.expect(parser_period)  # type: ignore[untyped-decorator]
    @login_required  # type: ignore[untyped-decorator]
    def get(self) -> dict[str, Any]:
        """
        Retrieve torrent statistics grouped by source.

        Fetches aggregated file counts and total sizes per source from the cache
        or database, then wraps the dataset into a standard API response envelope.

        Returns:
            dict[str, Any]: Envelope containing source statistics, metadata,
                and total element count.
        """
        args = parser_period.parse_args()
        start_date = args.get("start_date")
        end_date = args.get("end_date")

        stats = _get_stats_by_source(start_date, end_date)

        return self.build_envelope(stats, data_total=len(stats), type="StatsSource")


@cache.memoize(timeout=300)
def _get_stats_by_source(start_date: date | None, end_date: date | None) -> list[dict[str, object]]:
    """
    Fetch torrent statistics grouped by source within an optional date range.

    Executes the database query to aggregate torrent statistics by source domain
    filtered by date boundaries if provided, then caches the result using Flask-Caching memoization[cite: 2].

    Args:
        start_date (date | None, optional): Optional lower date boundary for filtering. Defaults to None.
        end_date (date | None, optional): Optional upper date boundary for filtering. Defaults to None.

    Returns:
        list[dict[str, object]]: A list of dictionaries containing source statistics,
            including total counts and associated sizes[cite: 2].
    """
    return Torrent.get_stats_by_source(start_date, end_date)
