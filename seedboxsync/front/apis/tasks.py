#
# Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
"""SeedboxSync API Task view."""
from typing import Any
from flask_restx import Namespace
from seedboxsync.front.apis import Resource

api = Namespace("tasks", description="Operations related to task lauching")


TASK_HANDLERS = {
    "seedbox": "seedboxsync.core.taskmanager.task.task_sync_seedbox.sync_seedbox",
    "blackhole": "seedboxsync.core.taskmanager.task.task_sync_blackhole.sync_blackhole",
}


@api.route("/<string:key>")
@api.response(404, "Task not found")
@api.param("key", "The task key")
class Tasks(Resource):
    """Endpoint for managing task lauching."""

    @api.doc("post_task")  # type: ignore[untyped-decorator]
    @api.response(202, "Task launched")  # type: ignore[untyped-decorator]
    def post(self, key: str) -> tuple[dict[str, Any], int]:
        """
        Launch a task associated with a task key.

        Args:
            key (str): Task identifier.

        Returns:
            tuple[dict[str, Any], int]: API response body and HTTP status code.
        """
        handler_path = TASK_HANDLERS.get(key)
        if handler_path is None:
            api.abort(404, f"Task '{key}' not found")

        assert handler_path is not None
        module_name, func_name = handler_path.rsplit(".", 1)
        module = __import__(module_name, fromlist=[func_name])
        task_func = getattr(module, func_name)

        # If these are Huey tasks, prefer enqueueing instead of calling directly.
        task_func()

        return {"status": "queued", "task": key}, 202
