# -*- coding: utf-8 -*-
#
# Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
"""
Transport client using FTP protocol.
"""

import ftplib
import ftputil
import ftputil.error
from typing import Any, Generator, List, Tuple
from seedboxsync.core import Flask, current_app
from seedboxsync.core.sync import AbstractSyncClient, _Callback
from seedboxsync.cli.exception import ConnectionError


class FtpSession(ftplib.FTP):
    """
    FTP session factory for ftputil with explicit port and timeout support.
    """

    def __init__(self, host: str, user: str, password: str, port: int = 21, timeout: float = -999):
        super().__init__()
        self.connect(host, port, timeout=timeout)
        self.login(user, password)


class FtpClient(AbstractSyncClient):
    """
    FTP transport client using ftputil.

    Handles file transfers between NAS and Seedbox servers. Provides basic
    operations such as get, put, rename, chmod, and directory traversal.
    """

    app: Flask
    _host: str
    _login: str
    _password: str
    _port: str
    _timeout: str | bool
    _client: Any | None

    def __init__(self) -> None:
        """
        Initialize the FTP client with connection parameters.

        Args:
            app (Flask): The Flask application instance.
        """
        self.app = current_app

        # Get config
        config = self.app.seedboxsync_config

        self._host = config.get("seedbox_host") or ""
        self._login = config.get("seedbox_login") or ""
        self._password = config.get("seedbox_password") or ""
        self._port = config.get("seedbox_port") or "21"
        self._timeout = config.get("seedbox_timeout") or False
        self._client = None

    def _connect_before(self) -> Any:
        """
        Initialize the FTP client if not already connected.

        Raises:
            ConnectionError: If connection or authentication fails.
        """
        if self._client is None:
            self.app.logger.debug("Init ftputil.FTPHost")
            try:
                self._client = ftputil.FTPHost(
                    self._host,
                    self._login,
                    self._password,
                    port=int(self._port),
                    timeout=self._normalize_timeout(),
                    session_factory=FtpSession,
                )
            except (
                ftputil.error.FTPError,
                ftplib.Error,
                OSError,
                EOFError,
                ValueError,
            ) as exc:
                raise ConnectionError(f"{str(exc)}\nFailed to establish a connection. " "Ensure the host, port, login and password are correct.")

        return self._client

    def _normalize_timeout(self) -> float | None:
        """
        Convert the configured timeout into a socket-compatible value.
        """
        if self._timeout is False or self._timeout is None:
            return None

        if isinstance(self._timeout, str):
            timeout = self._timeout.strip()
            if timeout == "" or timeout.lower() in ("false", "none", "null"):
                return None
            return float(timeout)

        return None

    def put(self, local_path: str, remote_path: str) -> None:
        """
        Upload a local file to the FTP server.

        Args:
            local_path (str): Path to the local file.
            remote_path (str): Destination path on the server (including filename).
        """
        client = self._connect_before()
        client.upload(local_path, remote_path)

    def get(
        self,
        remote_path: str,
        local_path: str,
        progress_callback: _Callback | None = None,
    ) -> None:
        """
        Download a remote file from the FTP server.

        Args:
            remote_path (str): Path of the remote file.
            local_path (str): Destination path on the local host.
            progress_callback (_Callback | None): Optional callback receiving bytes_transferred and total_bytes.
        """
        client = self._connect_before()

        if progress_callback is None:
            client.download(remote_path, local_path)
            return

        total_size = client.stat(remote_path).st_size
        transferred = 0
        ftp_session = client._session  # noqa: SLF001 - ftputil internal session used to access retrbinary.

        with open(local_path, "wb") as local_file:

            def on_block(data: bytes) -> None:
                nonlocal transferred
                local_file.write(data)
                transferred += len(data)
                progress_callback(transferred, total_size)

            ftp_session.retrbinary(
                f"RETR {remote_path}",
                on_block,
            )

    def stat(self, filepath: str) -> Any:
        """
        Retrieve metadata for a remote file.

        Args:
            filepath (str): Remote file path.

        Returns:
            Any: Object with attributes similar to Python's os.stat.
        """
        client = self._connect_before()
        return client.stat(filepath)

    def chdir(self, path: str | None = None) -> None:
        """
        Change the current working directory of the FTP session.

        Args:
            path (Optional[str]): Target directory. If None, no change occurs.
        """
        client = self._connect_before()
        if path is not None:
            client.chdir(path)

    def chmod(self, path: str, mode: int) -> None:
        """
        Change the mode (permissions) of a remote file.

        Args:
            path (str): Path of the file.
            mode (int): Unix-style permissions (like os.chmod).
        """
        client = self._connect_before()
        client.chmod(path, mode)

    def rename(self, old_path: str, new_path: str) -> None:
        """
        Rename a file or directory on the remote server.

        Args:
            old_path (str): Existing path.
            new_path (str): New path.
        """
        client = self._connect_before()
        client.rename(old_path, new_path)

    def walk(self, remote_path: str) -> Generator[Tuple[str, List[str], List[str]], None, None]:
        """
        Walk through remote directories, yielding paths, folders, and files.

        Args:
            remote_path (str): Remote directory to traverse.

        Yields:
            Tuple[str, List[str], List[str]]: (current_path, folders, files)
        """
        client = self._connect_before()
        walk_path = remote_path if remote_path != "" else client.curdir
        for path, folders, files in client.walk(walk_path):
            if remote_path == "":
                path = self._remove_current_directory_prefix(client, path)
            yield path, folders, files

    @staticmethod
    def _remove_current_directory_prefix(client: Any, path: str) -> str:
        """
        Keep FTP walk paths compatible with SftpClient.walk('').
        """
        if path == client.curdir:
            return ""

        prefix = client.curdir + client.sep
        if path.startswith(prefix):
            return path[len(prefix):]

        return path

    def close(self) -> None:
        """
        Close the FTP client and underlying connection.
        """
        if self._client is not None:
            self.app.logger.debug("Close ftputil.FTPHost client")
            self._client.close()
            self._client = None
