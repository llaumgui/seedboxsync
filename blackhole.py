#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
# SeedboxSync blackhole:
# Sync a local black hole (ie: NAS folder) with the black hole of your seedbox
# over sFTP.
#
# Copyright (C) 2015 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# This file is part of SeedboxSync.  SeedboxSync is free software: you can
# redistribute it and/or modify it under the terms of the GNU General Public
# License as published by the Free Software Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

__author__ = "llaumgui"

import ConfigParser
import logging
import glob
import os
try:
    import paramiko
except ImportError:
    print('Install paramiko first !\n\tpip install paramiko\n\t\tor\n\tapt-get install python2-paramiko\n\t\tor\n\tetc.')
    exit(1)

# Where to fin seedbox.ini ?
CONF_PATH = "/opt/llaumgui/seedbox-sync/seedbox.ini"


#
# BlackHoleSync class
#
class BlackHoleSync(object):
    """
    Class allows to sync local black hole (NAS ?) with the SeedBox black hole
    over sFTP
    """

    def __init__(self):
        """Constructor: initialize the synchronization"""

        # Load configuration
        self.config = ConfigParser.ConfigParser()
        self.config.read(CONF_PATH)

        # Load and configure logging
        try:
            logging.basicConfig(format='%(asctime)s %(levelname)s %(process)d - %(message)s',
                                filename=self.config.get('Log', 'blackhole_file_path'),
                                level=eval('logging.' + self.config.get('Log', 'blackhole_level')))
            logging.debug('Start BlackHoleSync')
        except Exception, e:
            logging.error(str(e))
            print(str(e))
            exit(2)

        # Set transport
        self.transport = False
        self.transport_client = False


    def __lock(self):
        """Lock task"""
        try:
            logging.debug('Lock task by ' + self.config.get('PID', 'blackhole_path'))
            lock = open(self.config.get('PID', 'blackhole_path'), 'w+')
            lock.write(str(os.getpid()))
            lock.close()
        except Exception, e:
            logging.error(str(e))
            print(str(e))
            exit(3)


    def __unlock(self):
        """Unlock task"""
        logging.debug('Unlock task by ' + self.config.get('PID', 'blackhole_path'))
        os.remove(self.config.get('PID', 'blackhole_path'))


    def is_locked(self):
        """Test if task is locked"""

        if os.path.isfile(self.config.get('PID', 'blackhole_path')):
            logging.info('Already running')
            return True

        logging.debug('Task is unlocked')
        return False


    def __init_transport_client(self):
        """Init transport and client"""
        try:
            logging.debug('Get paramiko.Transport')
            self.transport = paramiko.Transport((self.config.get('Seedbox', 'transfer_host'),
                                                 int(self.config.get('Seedbox', 'transfer_port'))))
            self.transport.connect(username=self.config.get('Seedbox', 'transfer_login'),
                                   password=self.config.get('Seedbox', 'transfer_password'))
            self.transport_client = paramiko.SFTPClient.from_transport(self.transport)

        except Exception, e:
            logging.error('Connection fail: ' + str(e))
            print('Connection fail: ' + str(e))
            self.__unlock()
            exit(4)


    def __close_transport(self):
        """Close transport client"""
        logging.debug('Close paramiko.Transport client')
        self.transport.close()


    def __upload_torrent(self, torrent):
        """Upload a torrent"""

        try:
            torrent_name = os.path.basename(torrent)
            logging.info('Upload "' + torrent_name + '"')

            logging.debug('Upload "' + torrent + '" in "' + self.config.get('Seedbox', 'tmp_path') + '" directory')
            self.transport_client.put(torrent,
                                      os.path.join(self.config.get('Seedbox', 'tmp_path'), torrent_name))

            # Chmod
            if self.config.get('Seedbox', 'transfer_chmod') != "false":
                logging.debug('Change mod in ' + self.config.get('Seedbox', 'transfer_chmod'))
                self.transport_client.chmod(os.path.join(self.config.get('Seedbox', 'tmp_path'), torrent_name),
                                            int(self.config.get('Seedbox', 'transfer_chmod'), 8))

            # Move from tmp
            logging.debug('Move from "' + self.config.get('Seedbox', 'tmp_path') + '" to "' + self.config.get('Seedbox', 'watch_path') + '"')
            self.transport_client.rename(os.path.join(self.config.get('Seedbox', 'tmp_path'), torrent_name),
                                         os.path.join(self.config.get('Seedbox', 'watch_path'), torrent_name))

            # Remove local torent
            logging.debug('Remove local torrent "' + torrent + '"')
            os.remove(torrent)

        except Exception, e:
            logging.error('Upload fail: ' + str(e))
            print('Upload fail: ' + str(e))


    def do_sync(self):
        """Do the synchronization"""

        # Create lock file.
        self.__lock()

        # Get all torrents
        torrents = glob.glob(self.config.get('Local', 'wath_path') + '/*.torrent')
        if len(torrents) > 0:
            # Upload torrents one by one
            self.__init_transport_client()
            for torrent in torrents:
                self.__upload_torrent(torrent)
            self.__close_transport()
        else:
            logging.info('No torrent in "' + self.config.get('Local', 'wath_path') + '"')

        # Remove lock file.
        self.__unlock()



# Go go go !
if __name__ == "__main__":
    sync = BlackHoleSync()

    if sync.is_locked():
        exit(0)
    else:
        sync.do_sync()

    exit(0)
