# -*- coding: utf-8 -*-
#
# Copyright (C) 2015-2020 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#

"""
Transport client using sFTP protocol.
"""
import os
from .abstract_client import AbstractClient
from stat import S_ISDIR
from cement import minimal_logger
import paramiko

LOG = minimal_logger(__name__)


class SftpClient(AbstractClient):
    """
    Transport from NAS to seedbox using sFTP paramiko library.
    """

    def __init__(self, host: str, login: str, password: str, port: str = "22", timeout: str = False):
        """
        Init transport and client.

        :param str host: the host of the server
        :param str login: the login to connect on the the server
        :param str password: the password to connect on the the server
        :param str port: the port of the server
        :param str timeout: the timeout for socket connection
        """
        self.__host = host
        self.__login = login
        self.__password = password
        self.__port = port
        self.__timeout = timeout
        self.__transport = None
        self.__client = None

    def __connect_before(self):
        """
        Init connection if not initialized.
        """
        if self.__transport is None:
            LOG.debug('Init paramiko.Transport')
            self.__transport = paramiko.Transport((self.__host, int(self.__port)))
            self.__transport.connect(username=self.__login, password=self.__password)
            self.__client = paramiko.SFTPClient.from_transport(self.__transport)

            # Setup timeout
            if self.__timeout:
                channel = self.__client.get_channel()
                channel.settimeout(self.__timeout)
                LOG.debug('Timeout is set to %s' % channel.gettimeout())

    def put(self, local_path: str, remote_path: str):
        """
        Copy a local file (``local_path``) to the SFTP server as ``remote_path``.

        :param str local_path: the local file to copy
        :param str remote_path: the destination path on the server. Note
            that the filename should be included. Only specifying a directory
            must result in an error.
        """
        self.__connect_before()
        return self.__client.put(local_path, remote_path)

    def get(self, remote_path: str, local_path: str):
        """
        Copy a remote file (``remote_path``) from the SFTP server to the local
        host as ``local_path``.

        :param str remote_path: the remote file to copy
        :param str local_path: the destination path on the local host
        """
        self.__connect_before()
        return self.__client.get(remote_path, local_path)

    def stat(self, filepath: str):
        """
        Retrieve informations about a file on the remote system.  The return
        value is an object whose attributes correspond to the attributes of
        Python's ``stat`` structure as returned by ``os.stat``, except that it
        contains fewer fields.  An SFTP server may return as much or as little
        info as it wants, so the results may vary from server to server.

        Unlike a Python `python:stat` object, the result may not be accessed as
        a tuple.  This is mostly due to the author's slack factor.
        The fields supported are: ``st_mode``, ``st_size``, ``st_uid``,
        ``st_gid``, ``st_atime``, and ``st_mtime``.

        :param str filepath: the filename to stat
        """
        self.__connect_before()
        return self.__client.stat(filepath)

    def chdir(self, path: str = None):
        """
        Change the "current directory" of this session.

        :param str path: new current working directory
        """
        self.__connect_before()
        return self.__client.chdir(path)

    def chmod(self, path: str, mode: str):
        """
        Change the mode (permissions) of a file. The permissions are unix-style
        and identical to those used by Python’s os.chmod function.

        :param str path: path of the file to change the permissions of
        :param int mode: new permissions
        """
        self.__connect_before()
        return self.__client.chmod(path, mode)

    def rename(self, old_path: str, new_path: str):
        """
        Rename a file or folder from ``old_path`` to ``new_path``.

        :param str old_path: existing name of the file or folder
        :param str new_path: new name for the file or folder
        """
        return self.__client.rename(old_path, new_path)

    # Code from https://gist.github.com/johnfink8/2190472
    def walk(self, remote_path: str):
        """
        Kindof a stripped down  version of os.walk, implemented for
        sftp.  Tried running it flat without the yields, but it really
        chokes on big directories.

        :param str remote_path: the remote path to list
        """
        self.__connect_before()
        path = remote_path
        files = []
        folders = []
        for f in self.__client.listdir_attr(remote_path):
            if S_ISDIR(f.st_mode):
                folders.append(f.filename)
            else:
                files.append(f.filename)
        yield path, folders, files

        for folder in folders:
            new_path = os.path.join(remote_path, folder)
            for x in self.walk(new_path):
                yield x

    def close(self):
        """
        Close transport client.
        """
        if self.__transport is not None:
            LOG.debug('Close paramiko.Transport client')
            return self.__transport.close()
