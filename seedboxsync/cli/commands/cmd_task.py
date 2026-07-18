# -*- coding: utf-8 -*-
#
# Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
"""
All commands related to the task queue manager operations.
"""

import click
from seedboxsync.cli import group, pass_context, Context
from seedboxsync.core.taskmanager.utils import load_task_modules


@group("task", help="Seedboxsync task operations.")  # type: ignore[untyped-decorator]
def cli() -> None:
    """Provide commands for task management."""
    pass


@cli.command("result", help="List results in the result store. Allows determining the currently running tasks.")  # type: ignore[untyped-decorator]
@pass_context
def tasks_result(ctx: Context) -> None:
    """List all_results() tasks."""

    data = []
    for task in ctx.app.task_manager.all_results():
        data.append([task])

    click.echo(ctx.render(data, headers=["Result key"]))


@cli.command("pending", help="List pending tasks.")  # type: ignore[untyped-decorator]
@pass_context
def tasks_pending(ctx: Context) -> None:
    """List pending tasks."""

    data = []
    for task in ctx.app.task_manager.pending():
        name = getattr(task, "name", str(task).split(": ")[0])
        task_id = getattr(task, "id", str(task).split(": ")[-1] if ": " in str(task) else str(task))
        data.append([name, task_id])

    click.echo(ctx.render(data, headers=["Task Name", "Task ID / UUID"]))


@cli.command("list", help="List registered tasks.")  # type: ignore[untyped-decorator]
@pass_context
def tasks_list(ctx: Context) -> None:
    """List registered tasks."""

    load_task_modules()
    data = []
    for task in ctx.app.task_manager._registry._registry.keys():
        data.append([task])

    click.echo(ctx.render(data, headers=["Class"]))
