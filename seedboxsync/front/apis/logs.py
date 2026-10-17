#
# Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
"""SeedboxSync API Logs view."""

from datetime import timedelta
from typing import Any
from flask_restx import Namespace, fields, reqparse
from seedboxsync.core.database.models import Log
from seedboxsync.front.apis import Resource, parser_pagination, parser_period
from seedboxsync.front.login_manager import admin_required

api = Namespace("logs", description="View logs information")


# ==========================
# Models
# ==========================
log_model = api.model(
    "Log",
    {
        "id": fields.Integer(
            required=True,
            description="Unique identifier of the log record",
            example=999,
        ),
        "level": fields.String(
            required=True,
            description="Severity level of the record (e.g. DEBUG, INFO, WARNING, ERROR, CRITICAL)",
            example="ConvallisMorbi.doc",
        ),
        "logger": fields.String(
            required=True,
            description="Name of the logger that emitted the record",
            example="doc",
        ),
        "module": fields.String(
            required=True,
            description="Module of the logger that emitted the record",
            example="doc",
        ),
        "message": fields.String(
            required=True,
            description="Formatted message recorded by the logger",
            example="ConvallisMorbi.doc",
        ),
        "timestamp": fields.DateTime(
            dt_format="iso8601",
            required=True,
            description="Date and time when the log record was created",
        ),
    },
)
log_list_envelope = Resource.build_envelope_model(api, "LogList", nested_model=log_model)
log_envelope = Resource.build_envelope_model(api, "Log", nested_model=log_model, as_list=False)
log_message_envelope = Resource.build_envelope_model(api, "LogMessage", as_message=True)


# ==========================
# Request parser
# ==========================
parser = reqparse.RequestParser()
parser.add_argument("search", type=str, required=False, help="Optional search string to filter items")
parser.add_argument("level", choices=("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"), required=False, help="Optional level to filter items")
parser.args.extend(parser_period.args)
parser.args.extend(parser_pagination.args)


# ==========================
# Endpoints
# ==========================
@api.route("")
class Logs(Resource):
    """Endpoint for managing log viewing."""

    @api.doc("list_logs")  # type: ignore[untyped-decorator]
    @api.expect(parser)  # type: ignore[untyped-decorator]
    @api.marshal_with(log_list_envelope, code=200, description="List of logs")  # type: ignore[untyped-decorator]
    @admin_required
    def get(self) -> dict[str, Any]:
        """
        Retrieve a list of recent logs.

        Query Parameters:
        - offset: Number of items to skip before starting to collect the result set (default: 0)
        - limit: Maximum number of logs to return (default=50)
        - search: Optional search string to filter items
        """
        args = parser.parse_args()
        offset = args.get("offset")
        limit = self.set_limit(args.get("limit", 50))
        search = args.get("search")
        level = args.get("level")
        start_date = args.get("start_date")
        end_date = args.get("end_date")

        count = Log.select()
        select = (
            Log.select(
                Log.id,
                Log.level,
                Log.logger,
                Log.module,
                Log.message,
                Log.timestamp,
            )
            .limit(limit)
            .offset(offset)
            .order_by(Log.timestamp.desc())
        )

        if search:
            count = count.where(Log.message.contains(search) | Log.level.contains(search) | Log.module.contains(search))
            select = select.where(Log.message.contains(search) | Log.level.contains(search) | Log.module.contains(search))

        if start_date:
            count = count.where(Log.timestamp >= start_date)
            select = select.where(Log.timestamp >= start_date)

        if level:
            count = count.where(Log.level == level)
            select = select.where(Log.level == level)

        if end_date:
            end_exclusive = end_date + timedelta(days=1)
            count = count.where(Log.timestamp < end_exclusive)
            select = select.where(Log.timestamp < end_exclusive)

        return self.build_envelope(list(select.dicts()), data_total=count.count(), type="LogList")
