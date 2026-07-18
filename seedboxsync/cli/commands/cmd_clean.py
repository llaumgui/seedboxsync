# -*- coding: utf-8 -*-
#
# Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
"""
All commands related to cleaning operations in SeedboxSync.
"""

import click
from seedboxsync.core.dao import Download


@click.group("clean", help="Cleaning operations.")
def cli() -> None:
    pass


@cli.command("progress", help="Clean the list of files currently in download from seedbox.")
def progress() -> None:
    """
    Remove all entries of files currently in download.

    This command deletes all records from the `Download` table where
    the download is not yet finished (`finished == 0`).

    Prints the number of deleted entries.
    """
    count = Download.delete().where(Download.finished == 0).execute()
    click.echo("In progress list cleaned. %s line(s) deleted" % count)


@cli.command("downloaded", help="Remove a downloaded file by ID to enable re-download.")
@click.argument("id", required=True, type=int)
def downloaded(id: int) -> None:
    """
    Remove a downloaded files by its ID.

    Allows the user to delete a specific downloaded torrent from
    the database, enabling it to be re-downloaded.

    Prints a message indicating whether the torrent was removed
    or if no matching ID was found.

    Args:
        id (int): The ID of the downloaded torrent to remove.
    """
    count = Download.delete().where(Download.id == id).execute()
    if count == 0:
        click.echo("No downloaded file with id %s" % id)
    else:
        click.echo("Torrent with id %s was removed" % id)
