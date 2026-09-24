#
# Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
"""All commands related to the task queue manager operations."""

import click
from seedboxsync.cli import Context, group, pass_context
from seedboxsync.core.taskmanager.utils import load_task_modules


@group("task", help="Task operations on task queue management.")  # type: ignore[untyped-decorator]
def cli() -> None:
    """Empty function for Click sub commands."""


@cli.command("result", help="List results in the result store. Allows determining the currently running tasks.")  # type: ignore[untyped-decorator]
@pass_context
def tasks_result(ctx: Context) -> None:
    """List all_results() tasks."""
    data = [{"key": task} for task in ctx.app.task_manager.all_results()]

    click.echo(ctx.render(data, headers={"key": "Result key"}))


@cli.command("pending", help="List pending tasks.")  # type: ignore[untyped-decorator]
@pass_context
def tasks_pending(ctx: Context) -> None:
    """List pending tasks."""
    data = []
    for task in ctx.app.task_manager.pending():
        task_str = str(task)
        data.append(
            {
                "name": getattr(task, "name", task_str.split(": ")[0]),
                "task_id": getattr(task, "id", str(task).split(": ")[-1] if ": " in task_str else task_str),
            }
        )

    click.echo(ctx.render(data, headers={"name": "Task Name", "task_id": "Task ID / UUID"}))


@cli.command("list", help="List registered tasks.")  # type: ignore[untyped-decorator]
@pass_context
def tasks_list(ctx: Context) -> None:
    """List registered tasks."""
    load_task_modules()
    data = [{"class": task} for task in ctx.app.task_manager._registry._registry]

    click.echo(ctx.render(data, headers={"class": "Class"}))


@cli.command("flush", help="Remove all data from the queue, schedule, and result store.")  # type: ignore[untyped-decorator]
@pass_context
def tasks_flush(ctx: Context) -> None:
    """Remove all data from the queue."""
    ctx.app.task_manager.flush()
    click.echo("Queue flushed")


@cli.command("flush-lock", help="Flush any locks that may be held.")  # type: ignore[untyped-decorator]
@pass_context
def tasks_flush_lock(ctx: Context) -> None:
    """Flush any locks that may be held."""
    ctx.app.task_manager.flush_locks()
    click.echo("Lock flushed")


@cli.command("sync-blackhole", help="Launch asynchrone task sync blackhole.")  # type: ignore[untyped-decorator]
@pass_context
def tasks_sync_blackhole(ctx: Context) -> None:
    """Launch asynchrone task sync blackhole."""
    with ctx.app.app_context():
        from seedboxsync.core.taskmanager.task.task_sync_blackhole import sync_blackhole

        sync_blackhole()
    click.echo("Task sync blackhole launched in task manager")


@cli.command("sync-seedbox", help="Launch asynchrone task sync seedbox.")  # type: ignore[untyped-decorator]
@pass_context
def tasks_sync_seedbox(ctx: Context) -> None:
    """Launch asynchrone task sync seedbox."""
    with ctx.app.app_context():
        from seedboxsync.core.taskmanager.task.task_sync_seedbox import sync_seedbox

        sync_seedbox()
    click.echo("Task sync seedbox launched in task manager")
