#
# Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
"""SeedboxSync api uploads stats view."""

from datetime import date
from typing import Any
from flask_restx import Namespace, fields
from seedboxsync.core.database.models import Torrent
from seedboxsync.front.apis import Resource, parser_period
from seedboxsync.front.cache import cache
from seedboxsync.front.login_manager import login_required

api = Namespace("uploads_stats", path="/uploads/stats", description="Stats related to uploads")


# ==========================
# Models
# ==========================
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
stats_source_envelope = Resource.build_envelope_model(api, "StatsSourceList", nested_model=stats_source_model)

stats_item_model = api.model(
    "UploadStatsItem",
    {
        "total": fields.Integer(
            description="Number of uploads",
            example=12,
        ),
        "size": fields.Integer(
            description="Total size of uploads in bytes",
            example=123456789,
        ),
        "human_size": fields.String(
            description="Human-readable total size of uploads",
            example="117.74 MB",
        ),
        "trend_total": fields.String(
            description="Trends vs. prior period for number of uploads",
            example="+10.0",
        ),
        "trend_size": fields.String(
            description="Trends vs. prior period for size of uploads",
            example="+15.2",
        ),
    },
)
stats_model = api.model(
    "UploadStats",
    {
        "day": fields.Nested(
            stats_item_model,
            description="Statistics for the current day",
        ),
        "week": fields.Nested(
            stats_item_model,
            description="Statistics for the current calendar week",
        ),
        "month": fields.Nested(
            stats_item_model,
            description="Statistics for the current month",
        ),
        "year": fields.Nested(
            stats_item_model,
            description="Statistics for the current year",
        ),
        "last24h": fields.Nested(
            stats_item_model,
            description="Statistics for the last 24 hours",
        ),
        "last7d": fields.Nested(
            stats_item_model,
            description="Statistics for the last 7 days",
        ),
        "last30d": fields.Nested(
            stats_item_model,
            description="Statistics for the last 30 days",
        ),
    },
)
stats_envelope = Resource.build_envelope_model(api, "UploadStats", nested_model=stats_model, as_list=False)


# ==========================
# Endpoints
# ==========================
@api.route("")
class UploadsStats(Resource):
    """Resource endpoint to retrieve torrents statistics."""

    @api.doc("stats_uploads")  # type: ignore[untyped-decorator]
    @api.marshal_with(stats_envelope, code=200, description="Uploads statistics")  # type: ignore[untyped-decorator]
    @login_required  # type: ignore[untyped-decorator]
    def get(self) -> dict[str, Any]:
        """
        Fetch overall upload statistics.

        Retrieves aggregated upload metrics and wraps them within
        a standard API response envelope[cite: 1, 2].

        Returns:
            dict[str, Any]: Formatted envelope response containing upload statistics[cite: 1, 2].
        """
        stats = _get_stats()
        return self.build_envelope(stats, data_total=len(stats), type="UploadStats")


@api.route("/source")
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

        return self.build_envelope(stats, data_total=len(stats), type="StatsSourceList")


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


@cache.memoize(timeout=300)
def _get_stats() -> dict[str, object]:
    """
    Fetch raw upload statistics within an optional date range from the database.

    Executes the underlying DAO query and caches the result for 5 minutes (300 seconds)
    using Flask-Caching memoization[cite: 1, 2, 3].

    Args:
        start_date (date | None): Optional start date filter for range querying[cite: 1].
        end_date (date | None): Optional end date filter for range querying[cite: 1].

    Returns:
        list[dict[str, object]]: A list of dictionaries representing upload statistics data[cite: 1, 2].
    """
    return Torrent.get_stats()
