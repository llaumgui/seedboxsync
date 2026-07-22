#
# Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
"""Transport client using FTP protocol."""

from collections.abc import Generator
import contextlib
import ftplib
from os import fspath
from pathlib import Path
from typing import Any
import ftputil
import ftputil.error
from seedboxsync.core import Flask, current_app
from seedboxsync.core.exception import SeedboxsyncConnectionError
from seedboxsync.core.sync import AbstractSyncClient, PathType, _Callback


class FtpSession(ftplib.FTP):
    """FTP session factory for ftputil with explicit port and timeout support."""

    def __init__(self, host: str, user: str, password: str, port: int = 21, timeout: float = -999) -> None:
        """
        Connect and authenticate an FTP session.

        Args:
            host (str): FTP server hostname.
            user (str): FTP account username.
            password (str): FTP account password.
            port (int): FTP server port.
            timeout (float): Connection timeout passed to ``ftplib``.
        """
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
        """Initialize the FTP client with application connection parameters."""
        self.app = current_app

        # Get config
        config = self.app.seedboxsync_config

        self._host = config.get("seedbox_host", "")
        self._login = config.get("seedbox_login", "")
        self._password = config.get("seedbox_password", "")
        self._port = config.get("seedbox_port", "21")
        self._timeout = config.get("seedbox_timeout", False)
        self._client = None

    def _connect_before(self) -> Any:
        """
        Initialize the FTP client if not already connected.

        Raises:
            SeedboxsyncConnectionError: If connection or authentication fails.
        """
        if self._client is None or self._client.closed:
            self.app.logger.debug("Init or reload ftputil.FTPHost")

            # Close inactive connecion
            if self._client is not None:
                with contextlib.suppress(Exception):
                    self._client.close()

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
                raise SeedboxsyncConnectionError(f"{exc!s}\nFailed to establish a connection. Ensure the host, port, login and password are correct.") from exc

        return self._client

    def _normalize_timeout(self) -> float | None:
        """Convert the configured timeout into a socket-compatible value."""
        if self._timeout is False or self._timeout is None:
            return None

        if isinstance(self._timeout, str):
            timeout = self._timeout.strip()
            if timeout == "" or timeout.lower() in ("false", "none", "null"):
                return None
            return float(timeout)

        return float(self._timeout)

    def put(self, local_path: PathType, remote_path: PathType) -> None:
        """
        Upload a local file to the FTP server.

        Args:
            local_path (PathType): Path to the local file.
            remote_path (PathType): Destination path on the server (including filename).
        """
        client = self._connect_before()
        local_path = fspath(local_path)
        remote_path = fspath(remote_path)
        client.upload(local_path, remote_path)

    def get(
        self,
        remote_path: PathType,
        local_path: PathType,
        progress_callback: _Callback | None = None,
    ) -> None:
        """
        Download a remote file from the FTP server.

        Args:
            remote_path (PathType): Path of the remote file.
            local_path (PathType): Destination path on the local host.
            progress_callback (_Callback | None): Optional callback receiving bytes_transferred and total_bytes.
        """
        client = self._connect_before()
        remote_path = fspath(remote_path)
        local_path = fspath(local_path)

        if progress_callback is None:
            client.download(remote_path, local_path)
            return

        total_size = client.stat(remote_path).st_size
        transferred = 0
        ftp_session = client._session

        with Path(local_path).open("wb") as local_file:

            def on_block(data: bytes) -> None:
                nonlocal transferred
                local_file.write(data)
                transferred += len(data)
                progress_callback(transferred, total_size)

            ftp_session.retrbinary(
                f"RETR {remote_path}",
                on_block,
            )

    def stat(self, filepath: PathType) -> Any:
        """
        Retrieve metadata for a remote file.

        Args:
            filepath (PathType): Remote file path.

        Returns:
            Any: Object with attributes similar to Python's os.stat.
        """
        client = self._connect_before()
        filepath = fspath(filepath)

        return client.stat(filepath)

    def chdir(self, path: PathType | None = None) -> None:
        """
        Change the current working directory of the FTP session.

        Args:
            path (Optional[PathType]): Target directory. If None, no change occurs.
        """
        client = self._connect_before()
        if path is not None:
            client.chdir(fspath(path))

    def chmod(self, path: PathType, mode: int) -> None:
        """
        Change the mode (permissions) of a remote file.

        Args:
            path (PathType): Path of the file.
            mode (int): Unix-style permissions (like os.chmod).
        """
        client = self._connect_before()
        path = fspath(path)
        client.chmod(path, mode)

    def rename(self, old_path: PathType, new_path: PathType) -> None:
        """
        Rename a file or directory on the remote server.

        Args:
            old_path (PathType): Existing path.
            new_path (PathType): New path.
        """
        client = self._connect_before()
        old_path = fspath(old_path)
        new_path = fspath(new_path)
        client.rename(old_path, new_path)

    def walk(self, remote_path: PathType) -> Generator[tuple[str, list[str], list[str]]]:
        """
        Walk through remote directories, yielding paths, folders, and files.

        Args:
            remote_path (PathType): Remote directory to traverse.

        Yields:
            tuple[str, list[str], list[str]]: (current_path, folders, files)
        """
        client = self._connect_before()
        remote_path = fspath(remote_path)
        walk_path = remote_path if remote_path != "" else client.curdir
        for path, folders, files in client.walk(walk_path):
            if remote_path == "":
                path = self._remove_current_directory_prefix(client, path)
            yield path, folders, files

    @staticmethod
    def _remove_current_directory_prefix(client: Any, path: str) -> str:
        """
        Keep FTP walk paths compatible with SftpClient.walk('').

        Args:
            client (Any): Active ``ftputil`` client.
            path (str): Path returned by ``ftputil``.

        Returns:
            str: Path relative to the current FTP directory.
        """
        if path == client.curdir:
            return ""

        prefix = client.curdir + client.sep
        if path.startswith(prefix):
            return path[len(prefix) :]

        return path

    def close(self) -> None:
        """Close the FTP client and underlying connection."""
        if self._client is not None:
            self.app.logger.debug("Close ftputil.FTPHost client")
            self._client.close()
            self._client = None
