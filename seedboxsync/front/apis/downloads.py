#
# Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
"""SeedboxSync api error module."""

from datetime import date
from typing import Any
from flask_restx import Namespace, fields, inputs, reqparse
from peewee import fn
from seedboxsync.core import utils
from seedboxsync.core.database.models import Download, typed_peewee_dicts
from seedboxsync.front.apis import DateTimeOrZero, Resource
from seedboxsync.front.cache import cache
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

stats_month_model = api.model(
    "StatsMonth",
    {
        "files": fields.Integer(
            required=True,
            description="Number of files downloaded in the month",
            example=135,
        ),
        "month": fields.String(
            required=True,
            description="Year and month of the statistics (format: yyyy-mm)",
            pattern=r"^\d{4}-(0[1-9]|1[0-2])$",
            example="2025-08",
        ),
        "total_size": fields.String(
            required=True,
            description="Total size of files downloaded",
            example="427.8GiB",
        ),
    },
)
stats_month_envelope = Resource.build_envelope_model(api, "StatsMonth", nested_model=stats_month_model)

stats_year_model = api.model(
    "StatsYear",
    {
        "files": fields.Integer(
            required=True,
            description="Number of files downloaded in the year",
            example=4989,
        ),
        "year": fields.String(
            required=True,
            description="Year of the statistics (format: yyyy)",
            pattern=r"^\d{4}$",
            example="2018",
        ),
        "total_size": fields.String(
            required=True,
            description="Total size of files downloaded",
            example="1476.5GiB",
        ),
    },
)
stats_year_envelope = Resource.build_envelope_model(api, "StatsYear", nested_model=stats_year_model)

stats_mimetype_model = api.model(
    "StatsMimeType",
    {
        "mime_type": fields.String(
            required=True,
            description="MIME type identifier detected for the files",
            pattern=r"^[a-zA-Z0-9!#$&^_\-\+\.]+/[a-zA-Z0-9!#$&^_\-\+\.]+$",
            example="video/x-matroska",
        ),
        "total": fields.Integer(
            required=True,
            description="Number or size of files downloaded for this MIME type",
            example=4989,
        ),
        "total_size": fields.Integer(
            required=True,
            description="Size of files downloaded for this MIME type",
            example=21678643250867,
        ),
        "human_total_size": fields.String(
            required=True,
            description="Total size of files downloaded with related humanization",
            example="19.7 Tio",
        ),
    },
)
stats_mimetype_envelope = Resource.build_envelope_model(api, "StatsMimeType", nested_model=stats_mimetype_model)


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

parser_period = reqparse.RequestParser()
parser_period.add_argument(
    "start_date",
    type=inputs.date_from_iso8601,
    location="args",
    help="Start date for filtering in ISO 8601 format (e.g. YYYY-MM-DD)",
)
parser_period.add_argument(
    "end_date",
    type=inputs.date_from_iso8601,
    location="args",
    help="End date for filtering in ISO 8601 format (e.g. YYYY-MM-DD)",
)


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

        return self.build_envelope(list(select.dicts()), data_total=count.count(), type="Download")


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


@api.route("/stats/month")
class DownloadsStatsByMonth(Resource):
    """Endpoint to retrieve monthly download statistics."""

    @api.doc("stats_downloads_by_month")  # type: ignore[untyped-decorator]
    @api.marshal_with(stats_month_envelope, code=200, description="Download statistics aggregated by month")  # type: ignore[untyped-decorator]
    @api.expect(parser_period)  # type: ignore[untyped-decorator]
    @login_required  # type: ignore[untyped-decorator]
    def get(self) -> dict[str, Any]:
        """
        Return download statistics grouped by month.

        Returns the number of files downloaded and total size per month.
        """
        args = parser_period.parse_args()
        start_date = args.get("start_date")
        end_date = args.get("end_date")

        stats = stats_by_period("month", start_date, end_date)

        return self.build_envelope(stats, data_total=len(stats), type="StatsMonth")


@api.route("/stats/year")
class DownloadsStatsByYear(Resource):
    """Endpoint to retrieve yearly download statistics."""

    @api.doc("stats_downloads_by_year")  # type: ignore[untyped-decorator]
    @api.marshal_with(stats_year_envelope, code=200, description="Download statistics aggregated by year")  # type: ignore[untyped-decorator]
    @login_required  # type: ignore[untyped-decorator]
    def get(self) -> dict[str, Any]:
        """
        Return download statistics grouped by year.

        Returns the number of files downloaded and total size per year.
        """
        stats = stats_by_period("year")

        return self.build_envelope(stats, data_total=len(stats), type="StatsYear")


@api.route("/stats/mimetype")
class DownloadsStatsByMimeType(Resource):
    """Resource endpoint to retrieve download MIME type statistics."""

    @api.doc("stats_downloads_by_mimetype")  # type: ignore[untyped-decorator]
    @api.marshal_with(stats_mimetype_envelope, code=200, description="Download statistics aggregated by mimetype")  # type: ignore[untyped-decorator]
    @api.expect(parser_period)  # type: ignore[untyped-decorator]
    @login_required  # type: ignore[untyped-decorator]
    def get(self) -> dict[str, Any]:
        """
        Retrieve download statistics grouped by MIME type.

        Fetches aggregated file counts and total sizes per MIME type from the cache
        or database, then wraps the dataset into a standard API response envelope.

        Returns:
            dict[str, Any]: Envelope containing MIME type statistics, metadata,
                and total element count.
        """
        args = parser_period.parse_args()
        start_date = args.get("start_date")
        end_date = args.get("end_date")

        stats = _get_stats_by_mime_type(start_date, end_date)

        return self.build_envelope(stats, data_total=len(stats), type="StatsMimeType")


# ==========================
# Utility functions
# ==========================
@cache.memoize(timeout=300)
def stats_by_period(period: str, start_date: date | None = None, end_date: date | None = None) -> list[dict[str, str | float]]:
    """
    Compute aggregated download statistics by period (month or year).

    Args:
        period (str): Aggregation period, either 'month' or 'year'.
        start_date (datetime.date | None): Optional start date filter.
        end_date (datetime.date | None): Optional end date filter.

    Returns:
        list[dict[str, str | float]]: List of statistics including period, number of files,
                                      and total size.
    """
    strftime_format = "%Y-%m" if period == "month" else "%Y"
    # Build "where" expression
    conditions = []
    conditions.append(Download.finished != 0)
    if start_date:
        conditions.append(Download.finished >= start_date)
    if end_date:
        conditions.append(Download.finished <= end_date)

    data = typed_peewee_dicts(
        Download.select(
            Download.id,
            Download.finished,
            fn.strftime(strftime_format, Download.finished).alias(period),
            Download.seedbox_size,
        )
        .where(*conditions)
        .order_by(Download.finished.desc())
        .dicts()
    )

    tmp = {}
    for download in data:
        key = download[period]
        size = download["seedbox_size"]
        if not key or not size:
            continue
        if key not in tmp:
            tmp[key] = {"files": 0, "total_size": 0.0}
        tmp[key]["files"] += 1
        tmp[key]["total_size"] += size

    return [
        {
            period: key,
            "files": tmp[key]["files"],
            "total_size": utils.byte_to_gi(tmp[key]["total_size"]),
        }
        for key in sorted(tmp)
    ]


@cache.memoize(timeout=300)
def _get_stats_by_mime_type(start_date: date | None, end_date: date | None) -> list[dict[str, object]]:
    """
    Fetch file download counts and total sizes grouped by MIME type.

    Executes the database query to aggregate finished downloads count and sum up
    their local sizes by MIME type, then caches the result using Flask-Caching memoization[cite: 3].

    Args:
        start_date (datetime.date | None): Optional start date filter.
        end_date (datetime.date | None): Optional end date filter.

    Returns:
        list[dict[str, object]]: A list of dictionaries containing MIME types,
            their associated total file counts, and total sizes in bytes[cite: 3].
    """
    return Download.get_stats_by_mime_type(start_date, end_date)
