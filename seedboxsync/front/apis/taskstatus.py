# -*- coding: utf-8 -*-
#
# Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
from flask_restx import fields, Namespace
from typing import Any
from seedboxsync.core.dao import TaskStatus
from seedboxsync.front.apis import DateTimeOrZero, Resource

api = Namespace("taskstatuses", description="Operations related to taskstatus")


# ==========================
# Models
# ==========================
taskstatus_model = api.model(
    "TaskStatuses",
    {
        "key": fields.String(
            required=True,
            description="Unique task identifier",
            example="sync_blackhole",
        ),
        "running": fields.Boolean(
            dt_format="iso8601",
            required=True,
            description="Whether the task is currently running",
            example=False,
        ),
        "started": DateTimeOrZero(
            dt_format="iso8601",
            required=False,
            description="Timestamp when the task execution started",
        ),
        "finished": DateTimeOrZero(
            dt_format="iso8601",
            required=True,
            description="Timestamp when the task execution finished",
        ),
    },
)
taskstatus_list_envelope = Resource.build_envelope_model(api, "TaskStatusList", nested_model=taskstatus_model)
taskstatus_envelope = Resource.build_envelope_model(api, "TaskStatus", nested_model=taskstatus_model, as_list=False)


# ==========================
# Endpoints
# ==========================
@api.route("")
class TaskStatusList(Resource):
    """
    Endpoint for managing taskstatus list.

    Provides a list of taskstatus.
    """

    @api.doc("list_taskstatus")  # type: ignore[untyped-decorator]
    @api.marshal_with(taskstatus_list_envelope, code=200, description="List of taskstatuses")  # type: ignore[untyped-decorator]
    def get(self) -> dict[str, Any]:
        """
        Retrieve a list of taskstatus.
        """
        select = TaskStatus.select(
            TaskStatus.key,
            TaskStatus.running,
            TaskStatus.started,
            TaskStatus.finished,
        )

        return self.build_envelope(list(select.dicts()), type="TaskStatus")


@api.route("/<string:key>")
@api.response(404, "TaskStatus not found")
@api.param("key", "The taskstatus key")
class TaskStatuses(Resource):
    """
    Endpoint for managing taskstatuses.

    Provides taskstatuses operations.
    """

    @api.doc("get_taskstatus")  # type: ignore[untyped-decorator]
    @api.marshal_with(taskstatus_envelope, code=200, description="TaskStatus element")  # type: ignore[untyped-decorator]
    def get(self, key: str) -> dict[str, Any]:
        """
        Retrieve a taskstatus.

        Args:
            key (str): TaskStatus identifier.

        Returns:
            dict[str, Any]: API response envelope containing the taskstatus.
        """
        try:
            select = (
                TaskStatus.select(
                    TaskStatus.key,
                    TaskStatus.running,
                    TaskStatus.started,
                    TaskStatus.finished,
                )
                .where(TaskStatus.key == key)
                .dicts()
                .get()
            )
        except TaskStatus.DoesNotExist:  # type: ignore[attr-defined]
            api.abort(404, "TaskStatus {} doesn't exist".format(key))

        return self.build_envelope(select, type="TaskStatus")
