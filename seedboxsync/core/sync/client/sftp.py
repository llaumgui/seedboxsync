# -*- coding: utf-8 -*-
#
# Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
"""
Transport client using sFTP protocol.
"""

import os
import paramiko
import socket
from stat import S_ISDIR
from typing import Generator, Tuple, List
from paramiko.sftp_attr import SFTPAttributes
from seedboxsync.core import Flask, current_app
from seedboxsync.core.sync import AbstractSyncClient, _Callback
from seedboxsync.cli.exception import ConnectionError


class SftpClient(AbstractSyncClient):
    """
    SFTP transport client using Paramiko.

    Handles file transfers between NAS and Seedbox servers. Provides basic
    operations such as get, put, rename, chmod, and directory traversal.
    """

    app: Flask
    _host: str
    _login: str
    _password: str
    _port: str
    _timeout: str | bool
    _transport = paramiko.Transport
    _client: paramiko.SFTPClient
    _max_concurrent_prefetch_requests: int

    def __init__(self) -> None:
        """
        Initialize the SFTP client with connection parameters.

        Args:
            app (Flask): The Flask application instance.
        """
        self.app = current_app

        # Get config
        config = self.app.seedboxsync_config

        self._host = config.get("seedbox_host") or ""
        self._login = config.get("seedbox_login") or ""
        self._password = config.get("seedbox_password") or ""
        self._port = config.get("seedbox_port") or ""
        self._timeout = config.get("seedbox_timeout") or False
        self._max_concurrent_prefetch_requests = int(config.get("seedbox_max_concurrent_prefetch_requests") or 128)
        self._transport = None

        self.app.logger.debug(f"Use sftp://{self._login}:****@{self._host}:{self._port}")

    def _connect_before(self) -> None:
        """
        Initialize the SFTP transport and client i   f not already connected.

        Raises:
            ConnectionError: If connection or authentication fails.
        """
        if self._transport is None:
            self.app.logger.debug("Init paramiko.Transport")
            try:
                self._transport = paramiko.Transport((self._host, int(self._port)))
            except (socket.gaierror, ConnectionRefusedError) as exc:
                raise ConnectionError(
                    f"{str(exc)}\nFailed to establish a connection. " + "Ensure the host and port are correct, and that no firewall is blocking access."
                )

            try:
                self._transport.connect(username=self._login, password=self._password)
            except paramiko.ssh_exception.AuthenticationException as exc:
                raise ConnectionError(f"{str(exc)}\nFailed to establish a connection. Ensure the login and password are correct.")

            self.app.logger.debug("Init paramiko.SFTPClient from transport")
            self._client = paramiko.SFTPClient.from_transport(self._transport)

            # Setup timeout
            if self._timeout:
                channel = self._client.get_channel()
                channel.settimeout(self._timeout)
                self.app.logger.debug("Timeout is set to %s" % channel.gettimeout())

    def put(self, local_path: str, remote_path: str) -> SFTPAttributes:
        """
        Upload a local file to the SFTP server.

        Args:
            local_path (str): Path to the local file.
            remote_path (str): Destination path on the server (including filename).

        Returns:
            SFTPAttributes: Metadata of the uploaded file.
        """
        self._connect_before()
        return self._client.put(local_path, remote_path)

    def get(
        self,
        remote_path: str,
        local_path: str,
        progress_callback: _Callback | None = None,
    ) -> None:
        """
        Download a remote file from the SFTP server.

        Args:
            remote_path (str): Path of the remote file.
            local_path (str): Destination path on the local host.
            progress_callback (_Callback | None): Optional callback receiving bytes_transferred.
        """
        self._connect_before()
        self._client.get(
            remote_path,
            local_path,
            callback=progress_callback,
            max_concurrent_prefetch_requests=self._max_concurrent_prefetch_requests,
        )

    def stat(self, filepath: str) -> SFTPAttributes:
        """
        Retrieve metadata for a remote file.

        Args:
            filepath (str): Remote file path.

        Returns:
            SFTPAttributes: Object with attributes similar to Python's os.stat:
                st_mode, st_size, st_uid, st_gid, st_atime, st_mtime.
        """
        self._connect_before()
        return self._client.stat(filepath)

    def chdir(self, path: str | None = None) -> None:
        """
        Change the current working directory of the SFTP session.

        Args:
            path (Optional[str]): Target directory. If None, no change occurs.
        """
        self._connect_before()
        self._client.chdir(path)

    def chmod(self, path: str, mode: int) -> None:
        """
        Change the mode (permissions) of a remote file.

        Args:
            path (str): Path of the file.
            mode (int): Unix-style permissions (like os.chmod).
        """
        self._connect_before()
        self._client.chmod(path, mode)

    def rename(self, old_path: str, new_path: str) -> None:
        """
        Rename a file or directory on the remote server.

        Args:
            old_path (str): Existing path.
            new_path (str): New path.
        """
        self._client.posix_rename(old_path, new_path)

    def walk(self, remote_path: str) -> Generator[Tuple[str, List[str], List[str]], None, None]:
        """
        Walk through remote directories, yielding paths, folders, and files.

        Args:
            remote_path (str): Remote directory to traverse.

        Yields:
            Tuple[str, List[str], List[str]]: (current_path, folders, files)

        Note:
            Simplified version of os.walk for SFTP. Efficient for large directories.

        Source:
            https://gist.github.com/johnfink8/2190472
        """
        self._connect_before()
        path = remote_path
        files: List[str] = []
        folders: List[str] = []
        for f in self._client.listdir_attr(remote_path):
            if S_ISDIR(f.st_mode):
                folders.append(f.filename)
            else:
                files.append(f.filename)
        yield path, folders, files

        for folder in folders:
            new_path = os.path.join(remote_path, folder)
            for x in self.walk(new_path):
                yield x

    def close(self) -> None:
        """
        Close the SFTP transport client and underlying connection.
        """
        if self._transport is not None:
            self.app.logger.debug("Close paramiko.Transport client")
            self._transport.close()
