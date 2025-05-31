# -*- coding: utf-8 -*-
#
# Copyright (C) 2015-2025 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#

"""
Transport client abstract class based on paramiko syntaxe.
"""

from abc import ABCMeta, abstractmethod
from cement.core.log import LogInterface


class AbstractClient():
    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self, log: LogInterface, host: str, login: str, password: str, port: str, timeout: str = False):
        """Init client.

        :param str log: the log interface
        :param str host: the host of the server
        :param str login: the login to connect on the the server
        :param str password: the password to connect on the the server
        :param str port: the port of the server
        :param str timeout: the timeout for socket connection
        """
        pass

    @abstractmethod
    def put(self, local_path: str, remote_path: str):
        """
        Copy a local file (``local_path``) to the server as ``remote_path``.

        :param str local_path: the local file to copy
        :param str remote_path: the destination path on the server. Note
            that the filename should be included. Only specifying a directory
            must result in an error.
        """
        pass

    @abstractmethod
    def get(self, remotep_path: str, local_path: str):
        """
        Copy a remote file (``remote_path``) from the server to the local
        host as ``local_path``.

        :param str remote_path: the remote file to copy
        :param str local_path: the destination path on the local host
        """
        pass

    @abstractmethod
    def stat(self, filepath: str):
        """
        Retrieve size about a file on the remote system.  The return
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
        pass

    @abstractmethod
    def chdir(self, path: str = None):
        """
        Change the "current directory" of this session.

        :param str path: new current working directory
        """
        pass

    @abstractmethod
    def chmod(self, path: str, mode: str):
        """
        Change the mode (permissions) of a file. The permissions are unix-style
        and identical to those used by Python’s os.chmod function.

        :param str path: path of the file to change the permissions of
        :param int mode: new permissions
        """
        pass

    @abstractmethod
    def rename(self, old_path: str, new_path: str):
        """
        Rename a file or folder from ``old_path`` to ``new_path``.

        :param str old_path: existing name of the file or folder
        :param str new_path: new name for the file or folder
        """
        pass

    @abstractmethod
    def close(self):
        """
        Close transport client.
        """
        pass
