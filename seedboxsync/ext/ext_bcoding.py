# -*- coding: utf-8 -*-
#
# Copyright (C) 2015-2025 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#

from bcoding import bdecode
from cement import App


class Bcoding(object):
    """
    Extends SeedboxSync with bcoding

    :param App app: the Cement App object
    """

    def __init__(self, app: App):
        self.app = app

    def get_torrent_infos(self, torrent_path: str):
        """
        Get information about a torrent file.

        :param str torrent_path: the path to the torrent file
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


def bcoding_post_setup_hook(app: App):
    """
    Extends SeedboxSync with bcoding

    :param App app: the Cement App object
    """
    app.log.debug('Extending seedboxsync application with bcoding')
    app.extend('bcoding', Bcoding(app))


def load(app: App):
    """Extension loader"""
    app.hook.register('post_setup', bcoding_post_setup_hook)
