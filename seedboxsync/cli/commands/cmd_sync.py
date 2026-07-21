#
# Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
"""All commands related to synchronization operations in SeedboxSync."""

import click
from huey.exceptions import TaskLockedException
from seedboxsync.cli import Context, group, pass_context
from seedboxsync.core.sync.services import (
    BLACKHOLE_LOCK_NAME,
    SEEDBOX_LOCK_NAME,
    blackhole as blackhole_service,
    seedbox as seedbox_service,
)


@group("sync", help="Run synchronization operations.")  # type: ignore[untyped-decorator]
def cli() -> None:
    """Empty function for Click sub commands."""


@cli.command("blackhole", help="Sync torrent from blackhole to seedbox.")  # type: ignore[untyped-decorator]
@click.option(
    "--dry-run",
    help="List only, do not upload or persist files.",
    is_flag=True,
    default=False,
)
@click.option(
    "-p",
    "--ping",
    help="Ping a service (e.g., Healthchecks) during execution.",
    is_flag=True,
    default=False,
)
@pass_context
def blackhole(ctx: Context, dry_run: bool, ping: bool) -> None:
    """
    Perform the blackhole synchronization.

    Args:
        ctx (Context): The Click context object.
        dry_run (bool): Whether to perform a dry run.
        ping (bool): Whether to ping a service during execution.
    """
    try:
        with ctx.app.task_manager.lock_task(BLACKHOLE_LOCK_NAME):
            blackhole_service(dry_run, ping)
    except TaskLockedException:
        ctx.app.logger.debug("Blackhole sync already running")


@cli.command("seedbox", help="Sync files from seedbox.")  # type: ignore[untyped-decorator]
@click.option(
    "--dry-run",
    help="List only, do not upload or persist files.",
    is_flag=True,
    default=False,
)
@click.option(
    "-p",
    "--ping",
    help="Ping a service (e.g., Healthchecks) during execution.",
    is_flag=True,
    default=False,
)
@click.option(
    "-o",
    "--only-store",
    help="Store the file list only, no download; useful for already synced seedbox.",
    is_flag=True,
    default=False,
)
@pass_context
def seedbox(ctx: Context, dry_run: bool, ping: bool, only_store: bool) -> None:
    """
    Perform synchronization from the seedbox.

    Args:
        ctx (Context): The Click context object.
        dry_run (bool): Whether to list files without downloading or persisting them.
        ping (bool): Whether to ping the configured monitoring service.
        only_store (bool): Whether to record remote files without downloading them.
    """
    """
    Perform the blackhole synchronization.

    Args:
        ctx (Context): The Click context object.
        dry_run (bool): Whether to perform a dry run.
        ping (bool): Whether to ping a service during execution.
    """
    try:
        with ctx.app.task_manager.lock_task(SEEDBOX_LOCK_NAME):
            seedbox_service(dry_run, ping, only_store)
    except TaskLockedException:
        ctx.app.logger.debug("Seedbox sync already running")
