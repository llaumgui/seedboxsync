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
from seedboxsync.core import utils
from seedboxsync.core.dao import Download, typed_peewee_dicts
from seedboxsync.front.apis import DateTimeOrZero, Resource
from seedboxsync.front.cache import cache

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
        limit = self.set_limit(args.get("limit"))
        search = args.get("search")
        finished = args.get("finished")

        count = Download.select()
        select = (
            Download.select(
                Download.id,
                Download.path,
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

        return self.build_envelope(list(select.dicts()), data_total=count.count(), type="Download")


@api.route("/progress")
class DownloadsProgress(Resource):
    """Endpoint for managing downloads progress."""

    @api.doc("delete_downloads_progress")  # type: ignore[untyped-decorator]
    @api.marshal_with(download_message_envelope, code=200, description="Downloads in progress deleted")  # type: ignore[untyped-decorator]
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
    @api.marshal_with(download_envelope, code=200, description="Download element")  # type: ignore[untyped-decorator]
    def get(self, id: int) -> dict[str, Any]:  # noqa: A002
        """
        Retrieve a download.

        Args:
            id (int): Download identifier.

        Returns:
            dict[str, Any]: API response envelope containing the download.
        """
        try:
            select = (
                Download.select(
                    Download.id,
                    Download.path,
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

    @cache.cached(timeout=3600)
    @api.doc("stats_downloads_by_month")  # type: ignore[untyped-decorator]
    @api.marshal_with(stats_month_envelope, code=200, description="Download statistics aggregated by month")  # type: ignore[untyped-decorator]
    def get(self) -> dict[str, Any]:
        """
        Return download statistics grouped by month.

        Returns the number of files downloaded and total size per month.
        """
        return self.build_envelope(stats_by_period("month"), type="StatsMonth")


@api.route("/stats/year")
class DownloadsStatsByYear(Resource):
    """Endpoint to retrieve yearly download statistics."""

    @cache.cached(timeout=3600)
    @api.doc("stats_downloads_by_year")  # type: ignore[untyped-decorator]
    @api.marshal_with(stats_year_envelope, code=200, description="Download statistics aggregated by year")  # type: ignore[untyped-decorator]
    def get(self) -> dict[str, Any]:
        """
        Return download statistics grouped by year.

        Returns the number of files downloaded and total size per year.
        """
        return self.build_envelope(stats_by_period("year"), type="StatsYear")


# ==========================
# Utility functions
# ==========================
def stats_by_period(period: str) -> list[dict[str, str | float]]:
    """
    Compute aggregated download statistics by period (month or year).

    Args:
        period (str): Aggregation period, either 'month' or 'year'.

    Returns:
        list[dict[str, str | float]]: List of statistics including period, number of files,
                                      and total size.
    """
    strftime_format = "%Y-%m" if period == "month" else "%Y"

    data = typed_peewee_dicts(
        Download.select(
            Download.id,
            Download.finished,
            fn.strftime(strftime_format, Download.finished).alias(period),
            Download.seedbox_size,
        )
        .where(Download.finished != 0)
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
