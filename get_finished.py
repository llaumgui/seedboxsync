#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
# SeedboxSync get_finished:
# Download over sFTP files from your Seedbox to your NAS and store files already
# in sqlite DB.
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

from stat import S_ISDIR
import ConfigParser
import logging
import glob
import os, errno
import sqlite3
import datetime
import codecs
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
# GetFinished class
#
class GetFinished(object):
    """
    Download over sFTP files from Seedbox to NAS and store files already downloaded
    """

    def __init__(self):
        """Constructor: initialize download"""

        # Load configuration
        self.config = ConfigParser.ConfigParser()
        self.config.readfp(codecs.open(CONF_PATH, "r", "utf8"))

        # Load and configure logging
        try:
            logging.basicConfig(format='%(asctime)s %(levelname)s %(process)d - %(message)s',
                                filename=self.config.get('Log', 'getfinished_file_path'),
                                level=eval('logging.' + self.config.get('Log', 'getfinished_level')))
            logging.debug('Start GetFinished')
        except Exception, e:
            logging.error(str(e))
            print(str(e))
            exit(2)

        # Set transport
        self.transport = False
        self.transport_client = False

        # Set database
        logging.info('Use dataBase ' + self.config.get('Local', 'sqlite_path'))
        if not os.path.exists(self.config.get('Local', 'sqlite_path')):
            self.db = sqlite3.connect(self.config.get('Local', 'sqlite_path'))
            self.dbcursor = self.db.cursor()
            self.__create_db()
        else:
            self.db = sqlite3.connect(self.config.get('Local', 'sqlite_path'))
            self.dbcursor = self.db.cursor()


    def __create_db(self):
        """Create initial database"""

        logging.info('DataBase ' + self.config.get('Local', 'sqlite_path') + 'not exists, need to be create')
        self.dbcursor.execute('''create table seedbox(conf string, value string)''')
        self.dbcursor.execute('''insert into seedbox(conf, value) values (?, ?)''', ('db_version', '1'))
        self.dbcursor.execute('''create table downloaded(id INTEGER PRIMARY KEY, path text, timestamp timestamp)''')
        self.db.commit()


    def __lock(self):
        """Lock task"""
        try:
            logging.debug('Lock task by ' + self.config.get('PID', 'getfinished_path'))
            lock = open(self.config.get('PID', 'getfinished_path'), 'w+')
            lock.write(str(os.getpid()))
            lock.close()
        except Exception, e:
            logging.error(str(e))
            print(str(e))
            self.db.close()
            exit(3)


    def __unlock(self):
        """Unlock task"""
        logging.debug('Unlock task by ' + self.config.get('PID', 'getfinished_path'))
        os.remove(self.config.get('PID', 'getfinished_path'))


    def is_locked(self):
        """Test if task is locked"""

        if os.path.isfile(self.config.get('PID', 'getfinished_path')):
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
            self.db.close()
            exit(4)


    def __close_transport(self):
        """Close transport client"""
        logging.debug('Close paramiko.Transport client')
        self.transport.close()


    def mkdir_p(self, path):
        """Like mkdir -p ;-)"""
        try:
            os.makedirs(path)
            logging.debug('Use local directory: "' + path + '"')
        except OSError as exc:
            if exc.errno == errno.EEXIST and os.path.isdir(path):
                pass
            else:
                raise


    def __get_file(self, filepath):
        """Download a torrent"""

        # Local path (without seedbox folder prefix)
        filepath_without_prefix = filepath.replace(self.config.get('Seedbox', 'finished_path').strip("/"), "", 1).strip("/")
        local_filepath = os.path.join(self.config.get('Local', 'download_path'), filepath_without_prefix)
        local_path = os.path.dirname(local_filepath)
        self.mkdir_p(local_path)

        try:
            logging.info('Download "' + filepath + '"')
            logging.debug('Download "' + filepath + '" in "' + local_path + '"')
            self.transport_client.get(filepath, local_filepath)

            # Store in database
            self.dbcursor.execute('''insert into downloaded(id, path, timestamp) values (NULL, ?, ?)''', (filepath, datetime.datetime.now()))
            self.db.commit()
        except Exception, e:
            logging.error('Upload fail: ' + str(e))
            print('Upload fail: ' + str(e))


    def __already_download(self, filepath):
        """Get in database if file was already downloaded"""
        self.dbcursor.execute('''SELECT count(*) FROM downloaded WHERE path=?''', [filepath])
        (number_of_rows,)=self.dbcursor.fetchone()
        if number_of_rows == 0:
            return False
        else:
            return True


    # Code from https://gist.github.com/johnfink8/2190472
    def __walk(self, remote_path):
        """Kindof a stripped down  version of os.walk, implemented for
        sftp.  Tried running it flat without the yields, but it really
        chokes on big directories."""

        path = remote_path
        files = []
        folders = []
        for f in self.transport_client.listdir_attr(remote_path):
            if S_ISDIR(f.st_mode):
                folders.append(f.filename)
            else:
                files.append(f.filename)
        yield path,folders,files

        for folder in folders:
            new_path=os.path.join(remote_path,folder)
            for x in self.__walk(new_path):
                yield x


    def get_new(self):
        """Do the synchronization"""

        # Create lock file.
        self.__lock()

        # Get transport
        self.__init_transport_client()

        remote_path = self.config.get('Seedbox', 'finished_path')
        logging.debug('Get file list in "' + remote_path + '"')

        # Get all files
        self.transport_client.chdir(os.path.split(remote_path)[0])
        parent = os.path.split(remote_path)[1]
        for walker in self.__walk(parent):
            for filename in walker[2]:
                filepath = os.path.join(walker[0],filename)
                if os.path.splitext(filename)[1] == self.config.get('Seedbox', 'part_suffix'):
                    logging.debug('Skip part file "' + filename + '"')
                elif self.__already_download(filepath):
                    logging.debug('Skip already downloaded "' + filename + '"')
                else:
                    self.__get_file(filepath)

        self.__close_transport
        self.db.close()

        # Remove lock file.
        self.__unlock()



# Go go go !
if __name__ == "__main__":
    dl = GetFinished()

    if dl.is_locked():
        exit(0)
    else:
        dl.get_new()

    exit(0)
