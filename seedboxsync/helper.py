# -*- coding: utf-8 -*-
#
# Copyright (C) 2015-2016 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#

"""
Helper module with helper classes.
"""

from __future__ import print_function
import logging
import os
import errno
import sqlite3
import bencode


#
# Helper class
#
class Helper(object):
    """
    Basic helper for Seedboxsync.
    """

    @staticmethod
    def mkdir_p(path):
        """
        Like a mkdir -p ;-).

        :param str path: the path to create
        """
        try:
            os.makedirs(path)
            logging.debug('Use local directory: "' + path + '"')
        except OSError as exc:
            if exc.errno == errno.EEXIST and os.path.isdir(path):
                pass
            else:
                raise

    @staticmethod
    def get_torrent_infos(torrent_path):
        """
        Get information about a torrent file.

        :param str torrent_path: the path to the torrent file
        """
        torrent = open(torrent_path, 'r')
        torrent_info = None

        try:
            torrent_info = bencode.bdecode(torrent.read())
        except bencode.BTL.BTFailure, exc:
            Helper.log_print('Not valid torrent: ' + str(exc), msg_type='error')
        finally:
            torrent.close()

        return torrent_info

    @classmethod
    def print(cls, *args):
        """
        Print outpout if not quiet.
        """
        if os.getenv('SEEDBOXSYNC_IS_QUIET', "False") != "True":
            print(*args)

    @classmethod
    def log_print(cls, message, msg_type='info'):
        """
        Log with logging in filesystem and print in console.

        :param str message: the message to print and log
        :param str msg_type: the type of message.
            Can be error, debug, warning or info.
        """
        if msg_type == 'error':
            logging.error(message)
            print(message)
        elif msg_type == 'debug':
            logging.debug(message)
            cls.print(message)
        elif msg_type == 'warning':
            logging.warning(message)
            print(message)
        else:
            logging.info(message)
            cls.print(message)


#
# SeedboxDbHelper class
#
class SeedboxDbHelper(object):
    """
    Store data in a sqlite database.
    """

    def __init__(self, database):
        """
        Initilize the database connection.
        """
        self.__database = database
        logging.debug('Use dataBase ' + self.__database)

        try:
            if not os.path.exists(self.__database):
                self.__db = sqlite3.connect(self.__database)
                self.cursor = self.__db.cursor()
                self.__create_db()
            else:
                self.__db = sqlite3.connect(self.__database)
                self.cursor = self.__db.cursor()
        except sqlite3.OperationalError, exc:
            Helper.log_print('SQLite fail: ' + str(exc), msg_type='error')
            exit()

    def __create_db(self):
        """
        Create initial database.
        """
        Helper.log_print('DataBase "' + self.__database + '" not exists, need to be create', msg_type='info')
        self.cursor.execute('''CREATE TABLE seedboxsync(key STRING, value STRING)''')
        self.cursor.execute('''INSERT INTO seedboxsync(key, value) VALUES (?, ?)''', ('db_version', '1'))
        self.cursor.execute('''CREATE TABLE torrent(id INTEGER PRIMARY KEY, name TEXT, announce TEXT, sent TIMESTAMP)''')
        self.cursor.execute('''CREATE TABLE download(
            id INTEGER PRIMARY KEY, path TEXT, seedbox_size INTEGER, local_size INTEGER, started TIMESTAMP, finished TIMESTAMP)''')
        self.commit()

    def commit(self):
        """
        Commit transaction in database.
        """
        self.__db.commit()

    def close(self):
        """
        Close database connection.
        """
        self.__db.close()
