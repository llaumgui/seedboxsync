#
# Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
"""SeedboxSync api error module."""

from datetime import date
from typing import Any
from flask_restx import Namespace, fields
from peewee import fn
from seedboxsync.core import utils
from seedboxsync.core.database.models import Download, typed_peewee_dicts
from seedboxsync.front.apis import Resource, parser_period
from seedboxsync.front.cache import cache
from seedboxsync.front.login_manager import login_required

api = Namespace("downloads_stats", path="/downloads/stats", description="Stats related to download")


# ==========================
# Models
# ==========================
stats_month_model = api.model(
    "DownloadStatsByMonth",
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
stats_month_envelope = Resource.build_envelope_model(api, "DownloadStatsByMonthList", nested_model=stats_month_model)

stats_year_model = api.model(
    "DownloadStatsByYear",
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
stats_year_envelope = Resource.build_envelope_model(api, "DownloadStatsByYearList", nested_model=stats_year_model)

stats_mimetype_model = api.model(
    "DownloadStatsByMimeType",
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
stats_mimetype_envelope = Resource.build_envelope_model(api, "DownloadStatsByMimeTypeList", nested_model=stats_mimetype_model)

stats_item_model = api.model(
    "DownloadStatsItem",
    {
        "total": fields.Integer(
            description="Number of downloads",
            example=12,
        ),
        "size": fields.Integer(
            description="Total size of downloads in bytes",
            example=123456789,
        ),
        "human_size": fields.String(
            description="Human-readable total size of downloads",
            example="117.74 MB",
        ),
    },
)
stats_model = api.model(
    "DownloadStats",
    {
        "day": fields.Nested(
            stats_item_model,
            description="Statistics for the current day",
        ),
        "week": fields.Nested(
            stats_item_model,
            description="Statistics for the current calendar week",
        ),
        "last7": fields.Nested(
            stats_item_model,
            description="Statistics for the last 7 calendar days",
        ),
        "month": fields.Nested(
            stats_item_model,
            description="Statistics for the current month",
        ),
        "year": fields.Nested(
            stats_item_model,
            description="Statistics for the current year",
        ),
    },
)
stats_envelope = Resource.build_envelope_model(api, "DownloadStats", nested_model=stats_model, as_list=False)


# ==========================
# Endpoints
# ==========================
@api.route("")
class DownloadsStats(Resource):
    """Resource endpoint to retrieve download statistics."""

    @api.doc("stats_downloads")  # type: ignore[untyped-decorator]
    @api.marshal_with(stats_envelope, code=200, description="Download statistics")  # type: ignore[untyped-decorator]
    @login_required  # type: ignore[untyped-decorator]
    def get(self) -> dict[str, Any]:
        """
        Fetch overall download statistics.

        Retrieves aggregated download metrics and wraps them within
        a standard API response envelope[cite: 1, 2].

        Returns:
            dict[str, Any]: Formatted envelope response containing download statistics[cite: 1, 2].
        """
        stats = _get_stats()
        return self.build_envelope(stats, data_total=len(stats), type="DownloadStats")


@api.route("/month")
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

        return self.build_envelope(stats, data_total=len(stats), type="DownloadStatsByMonthList")


@api.route("/year")
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

        return self.build_envelope(stats, data_total=len(stats), type="DownloadStatsByYearList")


@api.route("/mimetype")
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

        return self.build_envelope(stats, data_total=len(stats), type="DownloadStatsByMimeTypeList")


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


@cache.memoize(timeout=300)
def _get_stats() -> dict[str, object]:
    """
    Fetch raw download statistics within an optional date range from the database.

    Executes the underlying DAO query and caches the result for 5 minutes (300 seconds)
    using Flask-Caching memoization[cite: 1, 2, 3].

    Args:
        start_date (date | None): Optional start date filter for range querying[cite: 1].
        end_date (date | None): Optional end date filter for range querying[cite: 1].

    Returns:
        list[dict[str, object]]: A list of dictionaries representing download statistics data[cite: 1, 2].
    """
    return Download.get_stats()
