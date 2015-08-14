# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.

from stat import S_ISDIR
import logging
import paramiko
import os


#
# SeedboxSftpTransport.
#
class SeedboxSftpTransport(object):
    """
    Transport from NAS to seedbox using sFTP paramiko library.
    """

    def __init__(self, host, login, password, port="22"):
        """Init transport and client"""
        logging.debug('Get paramiko.Transport')
        self.__transport = paramiko.Transport((host, int(port)))
        self.__transport.connect(username=login, password=password)
        self.client = paramiko.SFTPClient.from_transport(self.__transport)

    # Code from https://gist.github.com/johnfink8/2190472
    def walk(self, remote_path):
        """
        Kindof a stripped down  version of os.walk, implemented for
        sftp.  Tried running it flat without the yields, but it really
        chokes on big directories.
        """
        path = remote_path
        files = []
        folders = []
        for f in self.client.listdir_attr(remote_path):
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
        logging.debug('Close paramiko.Transport client')
        self.__transport.close()
