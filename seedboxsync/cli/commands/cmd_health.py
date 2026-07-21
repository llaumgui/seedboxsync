#
# Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
"""All commands related to health checks in SeedboxSync."""

from datetime import datetime, timedelta
from urllib.error import URLError
from urllib.request import urlopen
import click
from seedboxsync.__version__ import __version__ as version
from seedboxsync.cli import Context, pass_context
from seedboxsync.core.dao import SeedboxSync, TaskStatus
from seedboxsync.core.utils import get_web_healthcheck_url


@click.command("health")
@pass_context
def cli(ctx: Context) -> None:
    """
    Show the health status of the SeedboxSync CLI and web service.

    Args:
        ctx (Context): The SeedboxSync Click context.
    """
    exit_code = 0

    # CLI part
    db_version = SeedboxSync.get_db_version()
    click.echo(f"Version: {version}")
    click.echo(f"Database version: {db_version}")
    click.secho("CLI - OK", fg="green")

    # Task manager part
    try:
        heartbeat = (
            TaskStatus.select(
                TaskStatus.key,
                TaskStatus.running,
                TaskStatus.started,
                TaskStatus.finished,
            )
            .where(TaskStatus.key == "heartbeat")
            .dicts()
            .first()
        )
    except TaskStatus.DoesNotExist:  # type: ignore[attr-defined]
        exit_code = 1

    if heartbeat is None:
        click.secho("Task manager - NOK", fg="red")
        exit_code = 2
    elif datetime.now() - heartbeat["finished"] > timedelta(minutes=5):
        click.secho("Task manager - NOK", fg="red")
        exit_code = 3
    else:
        click.secho("Task manager - OK", fg="green")

    # Flask WebUI part
    health_url = get_web_healthcheck_url()
    try:
        with urlopen(health_url, timeout=5) as response:
            if response.status == 200:
                click.secho("WebUI - OK", fg="green")
            else:
                click.secho("WebUI - NOK", fg="red")
                exit_code = 5
    except URLError:
        click.secho("WebUI - NOK", fg="red")
        exit_code = 6

    ctx.exit(exit_code)
