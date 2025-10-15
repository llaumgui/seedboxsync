# -*- coding: utf-8 -*-
#
# Copyright (C) 2015-2025 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
from bcoding import bdecode
from cement import App  # type: ignore[attr-defined]


class Bcoding(object):
    """
    Extension providing bcoding functionality for SeedboxSync.

    This class allows decoding and extracting information from torrent files.

    Attributes:
        app (App): The Cement App object instance.
    """

    def __init__(self, app: App):
        """Initializes the Bcoding extension.

        Args:
            app (App): The Cement App object.
        """
        self.app = app

    def get_torrent_infos(self, torrent_path: str) -> None | str:
        """
        xtracts information from a torrent file.

        Args:
            torrent_path (str): Path to the torrent file.

        Returns:
            str: Decoded torrent information.

        Raises:
            Exception: If the file is not a valid torrent.
        """
        with open(torrent_path, 'rb') as torrent:
            torrent_info = None

            try:
                torrent_info = bdecode(torrent.read())
            except Exception as exc:
                self.app.log.error('Not valid torrent: "%s"' + str(exc))
            finally:
                torrent.close()

            return torrent_info


def bcoding_post_setup_hook(app: App) -> None:
    """
    Post-setup hook to extend SeedboxSync with bcoding support.

    Args:
        app (App): The Cement App object.
    """
    app.log.debug('Extending seedboxsync application with bcoding')
    app.extend('bcoding', Bcoding(app))


def load(app: App) -> None:
    """
    Registers the bcoding extension in the Cement application.

    Args:
        app (App): The Cement App object.
    """
    app.hook.register('post_setup', bcoding_post_setup_hook)
