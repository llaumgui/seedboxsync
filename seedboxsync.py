#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
# Copyright (C) 2015 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#

'''
CLI of Seedboxsync.
'''

from __future__ import print_function
import argparse
import os
import sys

# If avalaible, insert local directories into path
if os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'seedboxsync')):
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

parser = argparse.ArgumentParser(description='Script for sync operations between your NAS and your seedbox.')

# Main applications
group = parser.add_mutually_exclusive_group()
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
parser.add_argument('-q', '--quiet', action='store_true')

# Go go go !
if __name__ == '__main__':
    args = parser.parse_args()

    # Set if quiet
    os.environ["SEEDBOXSYNC_IS_QUIET"] = str(args.quiet)

    if args.blackhole:
        from seedboxsync import BlackHoleSync
        sync = BlackHoleSync()
        if sync.is_locked():
            exit(0)
        else:
            sync.do_sync()

    elif args.download:
        from seedboxsync import DownloadSync
        sync = DownloadSync()
        if sync.is_locked():
            exit(0)
        else:
            sync.do_sync()

    elif args.lasts_torrents:
        from seedboxsync import GetInfos
        info = GetInfos()
        print(info.get_lasts_torrents(args.lasts_torrents))

    elif args.lasts_downloads:
        from seedboxsync import GetInfos
        info = GetInfos()
        print(info.get_lasts_downloads(args.lasts_downloads))

    elif args.unfinished_downloads:
        from seedboxsync import GetInfos
        info = GetInfos()
        print(info.get_unfinished_downloads())

    else:
        parser.print_help()

    exit(0)
