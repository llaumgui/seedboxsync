#
# Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
"""SeedboxSync taskmanager using Huey package."""

from .manager import Manager
from .track_taskstatus import heartbeat, heartbeat_shutdown, heartbeat_startup, track_taskstatus

__all__ = ["Manager", "heartbeat", "heartbeat_shutdown", "heartbeat_startup", "track_taskstatus"]

task_manager = Manager()
