# -*- coding: utf-8 -*-
#
# Copyright (C) 2015-2025 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
from cement import Controller, ex  # type: ignore[attr-defined]
from seedboxsync.core.dao import Download


class Clean(Controller):
    """
    Controller for cleaning operations in SeedboxSync.

    Provides commands to manage and remove torrents that are either
    in progress or already downloaded.
    """

    class Meta:
        help = 'all cleaning operations'
        label = 'clean'
        stacked_on = 'base'
        stacked_type = 'nested'

    @ex(help='clean the list of files currently in download from the seedbox')
    def progress(self) -> None:
        """
        Remove all entries of files currently in download.

        This command deletes all records from the `Download` table where
        the download is not yet finished (`finished == 0`).

        Prints the number of deleted entries.
        """
        count = Download.delete().where(Download.finished == 0).execute()
        self.app.print('In progress list cleaned. %s line(s) deleted' % count)  # type: ignore[attr-defined]

    @ex(
        help='remove a downloaded file by ID to enable re-download',
        arguments=[
            (
                [],
                {
                    'help': 'downloaded torrent ID to remove',
                    'action': 'store',
                    'dest': 'id'
                }
            )
        ]
    )
    def downloaded(self) -> None:
        """
        Remove a downloaded files by its ID.

        Allows the user to delete a specific downloaded torrent from
        the database, enabling it to be re-downloaded.

        Prints a message indicating whether the torrent was removed
        or if no matching ID was found.
        """
        count = Download.delete().where(Download.id == self.app.pargs.id).execute()
        if count == 0:
            self.app.print('No downloaded file with id %s' % self.app.pargs.id)  # type: ignore[attr-defined]
        else:
            self.app.print('Torrent with id %s was removed' % self.app.pargs.id)  # type: ignore[attr-defined]
