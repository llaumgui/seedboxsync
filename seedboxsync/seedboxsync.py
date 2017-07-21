# -*- coding: utf-8 -*-
#
# Copyright (C) 2015-2016 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#

"""
Main module of used by seedboxseed CLI.
"""

from __future__ import print_function, absolute_import
from seedboxsync.helper import (Helper, SeedboxDbHelper)
from prettytable import from_db_cursor
from importlib import import_module
import ConfigParser as configparser
import logging
import glob
import os
import argparse
import datetime


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

        self.__start()

    def __start(self):
        """
        Start CLI.
        """
        # Parse
        self.__args = self.__parser.parse_args()

        # Set if quiet
        os.environ["SEEDBOXSYNC_IS_QUIET"] = str(self.__args .quiet)

        if self.__args.blackhole:
            sync = BlackHoleSync()
            if sync.is_locked():
                exit(0)
            else:
                sync.do_sync()

        elif self.__args.download:
            sync = DownloadSync()
            if sync.is_locked():
                exit(0)
            else:
                sync.do_sync()

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

        exit(0)


#
# SeedboxSync main class
#
class SeedboxSync(object):
    """
    Super class for SeedboxSync projet.

    Exit code:
        - 0: All is good
        - 1: Import error
        - 2: Logging error
        - 3: Lock error
        - 4: connection error
        - 5: No configuration file found
    """

    CONF_PREFIX = None

    def __init__(self):
        """
        Main constructor: initialize the synchronization for child classes.
        """

        # Load configuration (seedbox.ini) from the good location
        self.__config_file = self.__get_config_file()

        # ConfigParser instance
        self._config = configparser.ConfigParser()
        self._config.read(self.__config_file)

        # Some path used by classes
        self.__lock_file = self._config.get('PID', self.CONF_PREFIX + 'path')
        self._db_path = self._config.get('Local', 'sqlite_path')
        self._finished_path = self._config.get('Seedbox', 'finished_path')

        # Load and configure logging
        self.__setup_logging()

        # Set empty transport
        self._transport_client = None

        # Set empty DB storage
        self._db = None

    def __get_config_file(self):
        """
        Load configuration from the good location:
            - seedboxsync folder
            - User folder (~)
            - /etc/seedboxsync
            - From environment variable SEEDBOXSYNC_CONF
        """
        config_file = None
        for location in os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'), \
                os.path.expanduser("~/.seedboxsync"), \
                '/usr/local/etc', '/usr/local/etc/seedboxsync', \
                '/etc', '/etc/seedboxsync', \
                os.environ.get('SEEDBOXSYNC_CONF'):
            try:
                seedbox_ini = os.path.join(location, 'seedboxsync.ini')
                if os.path.isfile(seedbox_ini):
                    config_file = seedbox_ini
                    break
            except:
                pass

        if config_file is None:
            print('No configuration file found !')
            exit(5)

        return config_file

    def __setup_logging(self):
        """
        Set the logging instance.

        See: https://docs.python.org/2/library/logging.html
        """
        try:
            logging.basicConfig(format='%(asctime)s %(levelname)s %(process)d - %(message)s',
                                filename=self._config.get('Log', self.CONF_PREFIX + 'file_path'),
                                level=eval('logging.' + self._config.get('Log', self.CONF_PREFIX + 'level')))
            logging.debug('Start')
            Helper.log_print('Load config from "' + self.__config_file + '"', msg_type='debug')
        except Exception, exc:
            Helper.log_print(str(exc), msg_type='error')
            exit(2)

    def _lock(self):
        """
        Lock task by a pid file to prevent launch two time.
        """
        logging.debug('Lock task by ' + self.__lock_file)
        try:
            lock = open(self.__lock_file, 'w+')
            lock.write(str(os.getpid()))
            lock.close()
        except Exception, exc:
            Helper.log_print(str(exc), msg_type='error')
            exit(3)

    def _unlock(self):
        """
        Unlock task, remove pid file.
        """
        logging.debug('Unlock task by ' + self.__lock_file)
        try:
            os.remove(self.__lock_file)
        except Exception, exc:
            Helper.log_print(str(exc), msg_type='error')

    def _check_pid(self, pid):
        """
        Check for the existence of a unix pid.

        :param int pid: the pid of the process
        """
        try:
            os.kill(pid, 0)
        except OSError:
            return False
        else:
            return True

    def is_locked(self):
        """
        Test if task is locked by a pid file to prevent launch two time.
        """
        if os.path.isfile(self.__lock_file):
            pid = int(file(self.__lock_file, 'r').readlines()[0])
            if self._check_pid(pid):
                Helper.log_print('Already running (pid=' + str(pid) + ')', msg_type='info')
                return True
            else:
                Helper.log_print('Restored from a previous crash (pid=' + str(pid) + ').', msg_type='warning')

        return False

    def _get_transport_client(self):
        """
        Init transport class. Currently only support sFTP.
        """
        transfer_protocol = self._config.get('Seedbox', 'transfer_protocol')
        client_class = 'Seedbox' + transfer_protocol.title() + 'Client'

        try:
            client_module = import_module('seedboxsync.transport_' + transfer_protocol)
        except ImportError:
            Helper.log_print('Unsupported protocole: ' + transfer_protocol, msg_type='error')
            self._unlock()
            exit(6)

        try:
            transfer_client = getattr(client_module, client_class)
        except AttributeError:
            Helper.log_print('Unsupported protocole module ! No class "' +
                             client_class + '" in module ' + 'seedboxsync.transport_' + transfer_protocol, msg_type='error')
            self._unlock()
            exit(7)

        try:
            return transfer_client(host=self._config.get('Seedbox', 'transfer_host'),
                                   port=int(self._config.get('Seedbox', 'transfer_port')),
                                   login=self._config.get('Seedbox', 'transfer_login'),
                                   password=self._config.get('Seedbox', 'transfer_password'))
        except Exception, exc:
            Helper.log_print('Connection fail: ' + str(exc), msg_type='error')
            self._unlock()
            exit(4)

    def _store_torrent_infos(self, torrent_path):
        """
        Get and store information about torrent.

        :param str torrent_path: the path to the torrent file
        """
        torrent_name = os.path.basename(torrent_path)
        torrent_info = Helper.get_torrent_infos(torrent_path)

        if torrent_info is not None:
            logging.debug('Torrent announce: "' + torrent_info['announce'] + '"')

            # Store torrent informations in torrent table
            self._db.cursor.execute('''INSERT INTO torrent(name, announce, sent) VALUES (?, ?, ?)''', (
                torrent_name, torrent_info['announce'], datetime.datetime.now()))
            self._db.commit()


#
# BlackHoleSync class
#
class BlackHoleSync(SeedboxSync):
    """
    Class which allows to sync a local black hole (ie: from a NAS) with a SeedBox
    black hole.
    """

    CONF_PREFIX = 'blackhole_'

    def __init__(self):
        """
        Constructor: initialize the blackhole synchronization.
        """
        # Call super class
        super(self.__class__, self).__init__()

    def __upload_torrent(self, torrent_path):
        """
        Upload a single torrent.

        :param str torrent_path: the path to the torrent file
        """

        torrent_name = os.path.basename(torrent_path)
        Helper.log_print('Upload "' + torrent_name + '"', msg_type='info')

        try:
            logging.debug('Upload "' + torrent_path + '" in "' + self._config.get('Seedbox', 'tmp_path') + '" directory')
            self._transport_client.put(torrent_path,  os.path.join(self._config.get('Seedbox', 'tmp_path'), torrent_name))

            # Chmod
            if self._config.get('Seedbox', 'transfer_chmod') != "false":
                logging.debug('Change mod in ' + self._config.get('Seedbox', 'transfer_chmod'))
                self._transport_client.chmod(os.path.join(self._config.get('Seedbox', 'tmp_path'), torrent_name),
                                             int(self._config.get('Seedbox', 'transfer_chmod'), 8))

            # Move from tmp
            logging.debug('Move from "' + self._config.get('Seedbox', 'tmp_path') + '" to "' + self._config.get('Seedbox', 'watch_path') + '"')
            self._transport_client.rename(os.path.join(self._config.get('Seedbox', 'tmp_path'), torrent_name),
                                          os.path.join(self._config.get('Seedbox', 'watch_path'), torrent_name))

            # Store in DB
            self._store_torrent_infos(torrent_path)

            # Remove local torent
            logging.debug('Remove local torrent "' + torrent_path + '"')
            os.remove(torrent_path)
        except Exception, exc:
            Helper.log_print(str(exc), msg_type='warning')

    def do_sync(self):
        """
        Do the blackhole synchronization.
        """
        # Create lock file.
        self._lock()

        # Get all torrents
        torrents = glob.glob(self._config.get('Local', 'watch_path') + '/*.torrent')
        if len(torrents) > 0:
            # Init transport_client
            self._transport_client = self._get_transport_client()

            # Init DB
            self._db = SeedboxDbHelper(self._db_path)

            # Upload torrents one by one
            for torrent in torrents:
                self.__upload_torrent(torrent)

            # Close resources
            self._transport_client.close()
            self._db.close()
        else:
            Helper.log_print('No torrent in "' + self._config.get('Local', 'watch_path') + '"', msg_type='info')

        # Remove lock file.
        self._unlock()


#
# GetFinished class
#
class DownloadSync(SeedboxSync):
    """
    Class which allows ti download files from Seedbox to NAS and store files
    already downloaded in a sqlite database.
    """

    CONF_PREFIX = 'download_'

    def __init__(self):
        """
        Constructor: initialize download.
        """
        # Call super class
        super(self.__class__, self).__init__()

    def __get_file(self, filepath):
        """
        Download a single file.

        :param str filepath: the filepath
        """
        # Local path (without seedbox folder prefix)
        filepath_without_prefix = filepath.replace(self._config.get('Seedbox', 'prefixed_path').strip("/"), "", 1).strip("/")
        local_filepath = os.path.join(self._config.get('Local', 'download_path'), filepath_without_prefix.encode('UTF8'))
        local_filepath_part = local_filepath + '.part'
        local_path = os.path.dirname(local_filepath)

        # Make folder tree
        Helper.mkdir_p(local_path)

        try:
            # Start timestamp in database
            seedbox_size = self._transport_client.stat(filepath).st_size
            if seedbox_size == 0:
                Helper.log_print('Empty file: "' + filepath + '" (' + str(seedbox_size) + ')', msg_type='warning')
                return False

            self._db.cursor.execute('''INSERT INTO download(path, seedbox_size, started) VALUES (?, ?, ?)''', (filepath, seedbox_size, datetime.datetime.now()))
            self._db.commit()
            download_id = self._db.cursor.lastrowid

            # Get file with ".part" suffix
            Helper.log_print('Download "' + filepath + '"', msg_type='info')
            self._transport_client.get(filepath, local_filepath_part)
            local_size = os.stat(local_filepath_part).st_size

            # Test size of the downloaded file
            if (local_size == 0) or (local_size != seedbox_size):
                Helper.log_print('Download fail: "' + filepath + '" (' + str(local_size) + '/' + str(seedbox_size) + ')', msg_type='error')
                return False

            # All is good ! Remove ".part" suffix
            os.rename(local_filepath_part, local_filepath)

            # Store in database
            self._db.cursor.execute('''UPDATE download SET local_size=?, finished=? WHERE id=?''', (
                local_size, datetime.datetime.now(), download_id))
            self._db.commit()
        except Exception, exc:
            Helper.log_print('Download fail: ' + str(exc), msg_type='error')

    def __is_already_download(self, filepath):
        """
        Get in database if file was already downloaded.

        :param str filepath: the filepath
        """
        self._db.cursor.execute('''SELECT count(*) FROM download WHERE path=? AND finished > 0''', [filepath])
        (number_of_rows,) = self._db.cursor.fetchone()
        if number_of_rows == 0:
            return False
        else:
            return True

    def do_sync(self):
        """
        Do the synchronization.
        """
        # Create lock file.
        self._lock()

        # Init transport_client
        self._transport_client = self._get_transport_client()

        # Init DB
        self._db = SeedboxDbHelper(self._db_path)

        Helper.log_print('Get file list in "' + self._finished_path + '"', msg_type='debug')

        # Get all files
        self._transport_client.chdir(os.path.split(self._finished_path)[0])
        parent = os.path.split(self._finished_path)[1]
        try:
            for walker in self._transport_client.walk(parent):
                for filename in walker[2]:
                    filepath = os.path.join(walker[0], filename)
                    if os.path.splitext(filename)[1] == self._config.get('Seedbox', 'part_suffix'):
                        Helper.log_print('Skip part file "' + filename + '"', msg_type='debug')
                    elif self.__is_already_download(filepath):
                        Helper.log_print('Skip already downloaded "' + filename + '"', msg_type='debug')
                    else:
                        self.__get_file(filepath)
        except IOError:
            Helper.log_print('Connection error.', msg_type='error')

        # Close resources
        self._transport_client.close()
        self._db.close()

        # Remove lock file.
        self._unlock()


#
# GetInfos class
#
class GetInfos(SeedboxSync):
    """
    Class which get informations about sync from database.
    """

    CONF_PREFIX = 'blackhole_'

    def __init__(self):
        """
        Constructor: initialize the blackhole synchronization.
        """
        # Call super class
        super(self.__class__, self).__init__()

        # Init DB
        self._db = SeedboxDbHelper(self._db_path)

    def get_lasts_torrents(self, number=10):
        """
        Get lasts "number" torrents from database.

        :param int number: number of torrents to display
        """
        self._db.cursor.execute('''SELECT id, name, sent FROM torrent ORDER BY sent DESC LIMIT ?''', [number])
        prettytable = from_db_cursor(self._db.cursor)
        self._db.close()

        return prettytable

    def get_lasts_downloads(self, number=10):
        """
        Get lasts "number" downloads from database.

        :param int number: number of torrents to display
        """
        self._db.cursor.execute('''SELECT id, DATETIME(finished) AS finished, SUBSTR(path, -100) AS path, local_size AS size
                                   FROM download
                                   ORDER BY finished DESC LIMIT ?''',
                                [number])
        prettytable = from_db_cursor(self._db.cursor)
        self._db.close()

        return prettytable

    def get_unfinished_downloads(self):
        """
        Get unfinished download from database.
        """
        self._db.cursor.execute('''SELECT id, DATETIME(started) AS started, SUBSTR(path, -100) AS path, seedbox_size AS size
                                   FROM download
                                   WHERE finished is null
                                   ORDER BY started DESC''')
        prettytable = from_db_cursor(self._db.cursor)
        self._db.close()

        return prettytable
