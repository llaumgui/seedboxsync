# -*- coding: utf-8 -*-
#
# Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
"""
All commands related to statistics operations in SeedboxSync.
"""

import click
import humanize
from peewee import fn
from seedboxsync.cli import group, pass_context, Context
from seedboxsync.core.dao import typed_peewee_dicts, Download


@group(
    "stats",
    help="Stats operations.",
    invoke_without_command=True,
    no_args_is_help=False,
)  # type: ignore[untyped-decorator]
@pass_context
def cli(ctx: Context) -> None:
    """
    Display statistics about completed downloads.

    Args:
        ctx (Context): The Click context object.
    """

    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())
        click.echo()
        ctx.invoke(total)


@cli.command("by-month", help="Show statistics aggregated by month.")  # type: ignore[untyped-decorator]
@pass_context
def by_month(ctx: Context) -> None:
    """
    Show statistics aggregated by month.

    Args:
        ctx (Context): The Click context object.
    """
    _stats_by_period(ctx, "month", "Month")


@cli.command("by-year", help="Show statistics aggregated by year.")  # type: ignore[untyped-decorator]
@pass_context
def by_year(ctx: Context) -> None:
    """
    Show statistics aggregated by year.

    Args:
        ctx (Context): The Click context object.
    """
    _stats_by_period(ctx, "year", "Year")


@cli.command("total", help="Show total statistics")  # type: ignore[untyped-decorator]
@pass_context
def total(ctx: Context) -> None:
    """
    Show total statistics for all completed downloads.

    Displays the total number of files and the total size.

    Args:
        ctx (Context): The Click context object.
    """
    query = Download.select().where(Download.finished != 0)
    total_files = query.count()
    total_size = sum([d.seedbox_size for d in query if d.seedbox_size])

    stats = [
        {
            "files": total_files,
            "total_size": humanize.filesize.naturalsize(total_size, True),
        }
    ]

    click.echo(ctx.render(stats, headers={"files": "Nb files", "total_size": "Total size"}))


def _stats_by_period(ctx: Context, period: str, header_label: str) -> None:
    """
    Generic helper to calculate statistics by a given period.

    Aggregates the number of files and total size for each month or year.

    Args:
        ctx (Context): The Click context object.
        period (str): Either 'month' or 'year' to group statistics.
        header_label (str): Label used for rendering the period column.
    """
    strftime_format = "%Y-%m" if period == "month" else "%Y"

    data = typed_peewee_dicts(
        Download.select(
            Download.id,
            Download.finished,
            fn.strftime(strftime_format, Download.finished).alias(period),
            Download.seedbox_size,
        )
        .where(Download.finished != 0)
        .order_by(Download.finished.desc())
        .dicts()
    )

    tmp = {}
    for download in data:
        key = download[period]
        size = download["seedbox_size"]
        if not key or not size:
            continue
        if key not in tmp:
            tmp[key] = {"files": 0, "total_size": 0.0}
        tmp[key]["files"] += 1
        tmp[key]["total_size"] += size

    stats = [
        {
            period: key,
            "files": tmp[key]["files"],
            "total_size": humanize.filesize.naturalsize(tmp[key]["total_size"], True),
        }
        for key in sorted(tmp)
    ]

    click.echo(
        ctx.render(
            stats,
            headers={
                period: header_label,
                "files": "Nb files",
                "total_size": "Total size",
            },
        )
    )
