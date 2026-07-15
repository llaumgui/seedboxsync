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
from seedboxsync.core.task.utils import load_task_modules


@group("task", help="Seedboxsync task operations.")  # type: ignore[untyped-decorator]
def cli() -> None:
    """Provide commands for task management."""
    pass


@cli.command("run-consumer", help="Run the task consumer.")  # type: ignore[untyped-decorator]
@click.option(
    "--workers",
    type=click.IntRange(min=1),
    default=1,
    show_default=True,
    help="Number of task workers.",
)
@click.option(
    "--worker-type",
    type=click.Choice(
        ["thread", "process", "greenlet"],
        case_sensitive=False,
    ),
    default="thread",
    show_default=True,
    help="Worker execution model.",
)
@click.option(
    "--periodic/--no-periodic",
    default=True,
    show_default=True,
    help="Enable periodic tasks.",
)
@pass_context
def huey_command(
    ctx: Context,
    workers: int,
    worker_type: str,
    periodic: bool,
) -> None:
    """Run the task consumer."""
    consumer = ctx.app.task_manager.create_consumer(
        workers=workers,
        worker_type=worker_type,
        periodic=periodic,
    )
    load_task_modules()
    ctx.app.logger.info("Task manager consumer loaded")

    consumer.run()
