#
# Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
"""SeedboxSync api error module."""

from typing import Any
from flask_restx import Namespace, fields, inputs, reqparse
from peewee import fn
from seedboxsync.core.database.models import Download
from seedboxsync.front.apis import DateTimeOrZero, Resource, parser_period
from seedboxsync.front.login_manager import login_required

api = Namespace("downloads", description="Operations related to download management")


# ==========================
# Models
# ==========================
download_model = api.model(
    "Download",
    {
        "id": fields.Integer(
            required=True,
            description="Unique identifier of the download record",
            example=999,
        ),
        "path": fields.String(
            required=True,
            description="Local path of the downloaded file",
            example="ConvallisMorbi.doc",
        ),
        "mime_extension": fields.String(
            required=True,
            description="File extension detected during MIME analysis",
            example="doc",
        ),
        "mime_type": fields.String(
            required=True,
            description="MIME type detected for the file (e.g. application/msword)",
            example="ConvallisMorbi.doc",
        ),
        "mime_confidence": fields.String(
            required=True,
            description="Confidence level or method used for MIME detection (e.g. extension, magic)",
            example="puremagic (confidence: 1)",
        ),
        "started": fields.DateTime(dt_format="iso8601", required=True, description="Download start timestamp"),
        "finished": DateTimeOrZero(
            dt_format="iso8601",
            required=False,
            description="Download completion timestamp",
        ),
        "local_size": fields.Integer(
            required=True,
            description="File size on local storage in bytes",
            example=3337353289,
        ),
        "human_local_size": fields.String(
            required=True,
            description="File size on local storage with related humanization",
            example="3.1 GiB",
        ),
        "seedbox_size": fields.Integer(
            required=True,
            description="File size on seedbox storage in bytes",
            example=3337353289,
        ),
        "human_seedbox_size": fields.String(
            required=True,
            description="File size on seedbox storage with related humanization",
            example="3.1 GiB",
        ),
        "progress": fields.Float(required=True, description="Download progress percentage", example=15.0),
    },
)
download_list_envelope = Resource.build_envelope_model(api, "DownloadList", nested_model=download_model)
download_envelope = Resource.build_envelope_model(api, "Download", nested_model=download_model, as_list=False)
download_message_envelope = Resource.build_envelope_model(api, "DownloadMessage", as_message=True)


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
    "finished",
    type=inputs.boolean,
    default=None,
    location="args",
    help="Filter only completed downloads (true) or in-progress downloads (false)",
)
parser.add_argument("search", type=str, required=False, help="Optional search string to filter items")
parser.args.extend(parser_period.args)


# ==========================
# Endpoints
# ==========================
@api.route("")
class DownloadsList(Resource):
    """
    Endpoint for managing downloads list.

    Provides a list of downloads with optional filtering for in-progress or completed files.
    """

    @api.doc("list_downloads")  # type: ignore[untyped-decorator]
    @api.expect(parser)  # type: ignore[untyped-decorator]
    @api.marshal_with(download_list_envelope, code=200, description="List of downloads")  # type: ignore[untyped-decorator]
    @login_required  # type: ignore[untyped-decorator]
    def get(self) -> dict[str, Any]:
        """
        Retrieve a list of recent downloads.

        Query Parameters:
        - offset: Number of items to skip before starting to collect the result set (default: 0)
        - limit: Maximum number of downloads to return (default=50)
        - search: Optional search string to filter items
        - finished: Filter downloads by status (false=in-progress, true=finished)
        """
        args = parser.parse_args()
        offset = args.get("offset")
        limit = self.set_limit(args.get("limit", 50))
        search = args.get("search")
        finished = args.get("finished")
        start_date = args.get("start_date")
        end_date = args.get("end_date")

        count = Download.select()
        select = (
            Download.select(
                Download.id,
                Download.path,
                Download.mime_extension,
                Download.mime_type,
                Download.mime_confidence,
                Download.started,
                Download.finished,
                Download.local_size,
                Download.seedbox_size,
                fn.humanize(Download.local_size).alias("human_local_size"),
                fn.humanize(Download.seedbox_size).alias("human_seedbox_size"),
                fn.round(
                    (Download.local_size.cast("REAL") / Download.seedbox_size.cast("REAL")) * 100,
                    2,
                ).alias("progress"),
            )
            .limit(limit)
            .offset(offset)
            .order_by(Download.finished.desc())
        )

        if search:
            count = count.where(Download.path.contains(search))
            select = select.where(Download.path.contains(search))

        if finished is not None:
            # Filter downloads by completion status
            if finished:
                count = count.where(Download.finished != 0)
                select = select.where(Download.finished != 0)
            else:
                count = count.where(Download.finished == 0)
                select = select.where(Download.finished == 0)

        if start_date:
            count = count.where(Download.finished >= start_date)
            select = select.where(Download.finished >= start_date)

        if end_date:
            count = count.where(Download.finished <= end_date)
            select = select.where(Download.finished <= end_date)

        return self.build_envelope(list(select.dicts()), data_total=count.count(), type="DownloadList")


@api.route("/progress")
class DownloadsProgress(Resource):
    """Endpoint for managing downloads progress."""

    @api.doc("delete_downloads_progress")  # type: ignore[untyped-decorator]
    @api.marshal_with(download_message_envelope, code=200, description="Downloads in progress deleted")  # type: ignore[untyped-decorator]
    @login_required  # type: ignore[untyped-decorator]
    def delete(self) -> dict[str, Any]:
        """Delete progress downloads."""
        count = Download.delete().where(Download.finished == 0).execute()
        return self.build_envelope(None, type="Download", message=f"{count} download(s) deleted.")


@api.route("/<int:id>")
@api.response(404, "Download not found")
@api.param("id", "The download identifier")
class Downloads(Resource):
    """
    Endpoint for managing downloads.

    Provides downloads operations.
    """

    @api.doc("get_download")  # type: ignore[untyped-decorator]
    @api.marshal_with(download_envelope, skip_none=True, code=200, description="Download element")  # type: ignore[untyped-decorator]
    @login_required  # type: ignore[untyped-decorator]
    def get(self, id: int) -> dict[str, Any]:  # noqa: A002
        """
        Retrieve a download.

        Args:
            id (int): Download identifier.

        Returns:
            dict[str, Any]: API response envelope containing the download.
        """
        select: Download | None = None
        try:
            select = (
                Download.select(
                    Download.id,
                    Download.path,
                    Download.mime_extension,
                    Download.mime_type,
                    Download.mime_confidence,
                    Download.started,
                    Download.finished,
                    Download.local_size,
                    Download.seedbox_size,
                    fn.humanize(Download.local_size).alias("human_local_size"),
                    fn.humanize(Download.seedbox_size).alias("human_seedbox_size"),
                    fn.round(
                        (Download.local_size.cast("REAL") / Download.seedbox_size.cast("REAL")) * 100,
                        2,
                    ).alias("progress"),
                )
                .where(Download.id == id)
                .dicts()
                .get()
            )
        except Download.DoesNotExist:  # type: ignore[attr-defined]
            api.abort(404, f"Download {id} doesn't exist")

        return self.build_envelope(select, type="Download")

    @api.doc("delete_download")  # type: ignore[untyped-decorator]
    @api.marshal_with(download_message_envelope, code=200, description="Delete download element")  # type: ignore[untyped-decorator]
    @login_required  # type: ignore[untyped-decorator]
    def delete(self, id: int) -> dict[str, Any]:  # noqa: A002
        """
        Delete a download.

        Args:
            id (int): Download identifier.

        Returns:
            dict[str, Any]: API response envelope containing a status message.
        """
        count = Download.delete().where(Download.id == id).execute()
        if count == 0:
            api.abort(404, f"Download {id} doesn't exist")

        return self.build_envelope(None, type="Download", message=f"Download {id} deleted.")
