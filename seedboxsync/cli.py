# -*- coding: utf-8 -*-
#
# Copyright (C) 2015-2018 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#

"""
CLI module.
"""

from seedboxsync.seedboxsync import (BlackHoleSync, DownloadSync, GetInfos)
from seedboxsync.exceptions import (ConfigurationException, IsLockedException)
import argparse
import os
import configparser


#
# CLI class
#
class CLI(object):
    """
    CLI interface.
    """

    def __init__(self):
        """
        CLI constructor.
        """
        self.__parser = argparse.ArgumentParser(description='Script for sync operations between your NAS and your seedbox.')

        # Mandatories arguments
        group = self.__parser.add_mutually_exclusive_group()
        group.add_argument('--blackhole', help='send torrent from the local blackhole to the seedbox blackhole',
                           action='store_true')
        group.add_argument('-t', '--lasts-torrents', help='get list of lasts torrents uploaded',
                           default=False, const=10, nargs='?', type=int,
                           action='store')
        group.add_argument('--download', help='download finished files from seedbox to NAS',
                           action='store_true')
        group.add_argument('-d', '--lasts-downloads', help='get list of lasts downloads',
                           default=False, const=10, nargs='?', type=int,
                           action='store')
        group.add_argument('-u', '--unfinished-downloads', help='get list of unfinished downloads',
                           action='store_true')

        # Optionnal arguments
        self.__parser.add_argument('-q', '--quiet', action='store_true')

        # Start but try / catch.
        try:
            self.__start()
        except configparser.NoSectionError as exc:
            raise ConfigurationException(str(exc))
        except configparser.NoOptionError as exc:
            raise ConfigurationException(str(exc))

    def __start(self):
        """
        Start CLI.
        """
        # Parse
        self.__args = self.__parser.parse_args()

        # Set if quiet
        os.environ["SEEDBOXSYNC_IS_QUIET"] = str(self.__args.quiet)

        if self.__args.blackhole:
            self.__call_blackhole_sync()
        elif self.__args.download:
            self.__call_download_sync()
        elif self.__args.lasts_torrents:
            info = GetInfos()
            print(info.get_lasts_torrents(self.__args.lasts_torrents))
        elif self.__args.lasts_downloads:
            info = GetInfos()
            print(info.get_lasts_downloads(self.__args.lasts_downloads))
        elif self.__args.unfinished_downloads:
            info = GetInfos()
            print(info.get_unfinished_downloads())
        else:
            self.__parser.print_help()

    def __call_download_sync(self):
        """
        Call DownloadSync method
        """
        sync = DownloadSync()
        if sync.is_locked():
            raise IsLockedException("SeedboxSync is locked")
        else:
            sync.do_sync()

    def __call_blackhole_sync(self):
        """
        Call BlackHoleSync method
        """

        sync = BlackHoleSync()
        if sync.is_locked():
            raise IsLockedException("SeedboxSync is locked")
        else:
            sync.do_sync()
