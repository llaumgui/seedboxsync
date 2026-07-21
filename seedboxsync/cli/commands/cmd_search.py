#
# Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
"""All commands related to search operations in SeedboxSync."""

import click
from peewee import fn
from seedboxsync.cli import Context, group, pass_context
from seedboxsync.core.dao import Download, Torrent, typed_peewee_dicts


@group("search", help="Search operations.")  # type: ignore[untyped-decorator]
@pass_context
def cli(ctx: Context) -> None:
    """Empty function for Click sub commands."""


@cli.command("uploaded", help="Search last torrents uploaded from blackhole.")  # type: ignore[untyped-decorator]
@click.option("-n", "--number", type=int, default=10, help="Number of torrents to display.")
@click.option("-s", "--search", help="Term to search.")
@pass_context
def uploaded(ctx: Context, number: int, search: str) -> None:
    """
    Search for the most recent torrents uploaded from blackhole.

    Filters torrents by an optional search term and limits
    the number of results displayed.

    Renders a list of torrent IDs, names, and sent timestamps.

    Args:
        ctx (Context): The Click context object.
        number (int): The maximum number of torrents to display.
        search (str): An optional search term to filter torrent names.
    """
    # Build "where" expression
    where = Torrent.name.contains(search) if search else ~Torrent.id.contains("not_a_int")

    # DB query
    data = Torrent.select(Torrent.id, Torrent.name, Torrent.sent).where(where).limit(number).order_by(Torrent.sent.desc()).dicts()

    click.echo(
        ctx.render(
            reversed(data),
            headers={"id": "Id", "name": "Name", "sent": "Sent datetime"},
            tablefmt="github",
        )
    )


@cli.command("downloaded", help="Search last files downloaded from seedbox.")  # type: ignore[untyped-decorator]
@click.option("-n", "--number", type=int, default=10, help="Number of torrents to display.")
@click.option("-s", "--search", help="Term to search.")
@pass_context
def downloaded(ctx: Context, number: int, search: str) -> None:
    """
    Search for the most recent files downloaded from the seedbox.

    Filters downloads by an optional search term and limits
    the number of results displayed.

    Renders a list of download IDs, paths, finished timestamps, and sizes.

    Args:
        ctx (Context): The Click context object.
        number (int): The maximum number of torrents to display.
        search (str): An optional search term to filter torrent names.
    """
    # Build "where" expression
    where = (Download.finished != 0) & Download.path.contains(search) if search else Download.finished != 0

    # DB query
    data = (
        Download.select(
            Download.id,
            fn.SUBSTR(Download.path, -100).alias("path"),
            Download.finished,
            fn.humanize(Download.local_size).alias("size"),
        )
        .where(where)
        .limit(number)
        .order_by(Download.finished.desc())
        .dicts()
    )

    click.echo(
        ctx.render(
            reversed(data),
            headers={
                "id": "Id",
                "finished": "Finished",
                "path": "Path",
                "size": "Size",
            },
            tablefmt="github",
        )
    )


@cli.command("progress", help="Search files currently in download from seedbox.")  # type: ignore[untyped-decorator]
@click.option("-n", "--number", type=int, default=10, help="Number of torrents to display.")
@click.option("-s", "--search", help="Term to search.")
@pass_context
def progress(ctx: Context, number: int, search: str) -> None:
    """
    Search for files currently in download from the seedbox.

    Filters in-progress downloads by an optional search term and limits
    the number of results displayed.

    Calculates local download progress and ETA, and renders a list
    including ID, path, start time, progress percentage, ETA, and size.

    Args:
        ctx (Context): The Click context object.
        number (int): The maximum number of torrents to display.
        search (str): An optional search term to filter torrent names.
    """
    # Build "where" expression
    where = (Download.finished == 0) & Download.path.contains(search) if search else Download.finished == 0

    # Calculate columns
    progress_expr = 100.0 * Download.local_size / fn.NULLIF(Download.seedbox_size, 0)
    eta_expr = (fn.STRFTIME("%s", "now", "localtime") - fn.STRFTIME("%s", Download.started)) * (100.0 - progress_expr) / fn.NULLIF(progress_expr, 0)

    # DB query
    data = typed_peewee_dicts(
        Download.select(
            Download.id,
            fn.SUBSTR(Download.path, -100).alias("path"),
            Download.started,
            fn.ROUND(progress_expr, 0).cast("INTEGER").concat("%").alias("progress"),
            fn.naturaldelta(eta_expr).alias("eta"),
            fn.humanize(Download.seedbox_size).alias("size"),
        )
        .where(where)
        .limit(number)
        .order_by(Download.started.desc())
        .dicts()
    )

    # Define the output column order explicitly
    rows = [
        (
            row["id"],
            row["path"],
            row["started"],
            row["progress"],
            row["eta"],
            row["size"],
        )
        for row in reversed(list(data))
    ]

    click.echo(
        ctx.render(
            rows,
            headers=["Id", "Path", "Started", "Progress", "ETA", "Size"],
            tablefmt="github",
        )
    )
