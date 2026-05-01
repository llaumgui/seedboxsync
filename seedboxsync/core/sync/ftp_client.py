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
from typing import Any, Generator, List, Tuple
import ftputil
import ftputil.error
from cement.core.log import LogInterface
from seedboxsync.core.sync.abstract_client import AbstractClient
from seedboxsync.core.sync.sync import ConnectionError


class FtpSession(ftplib.FTP):
    """
    FTP session factory for ftputil with explicit port and timeout support.
    """

    def __init__(self, host: str, user: str, password: str, port: int = 21, timeout: float = -999):
        super().__init__()
        self.connect(host, port, timeout=timeout)
        self.login(user, password)


class FtpClient(AbstractClient):
    """
    FTP transport client using ftputil.

    Handles file transfers between NAS and Seedbox servers. Provides basic
    operations such as get, put, rename, chmod, and directory traversal.
    """
    __log: LogInterface
    __host: str
    __login: str
    __password: str
    __port: str
    __timeout: str | bool
    __client: Any | None

    def __init__(
        self,
        log: LogInterface,
        host: str,
        login: str,
        password: str,
        port: str = "21",
        timeout: str | bool = False,
    ):
        """
        Initialize the FTP client with connection parameters.

        Args:
            log (LogInterface): Logger instance.
            host (str): FTP server hostname.
            login (str): Username for authentication.
            password (str): Password for authentication.
            port (str): Server port (default: '21').
            timeout (str | bool): Socket timeout in seconds (default: False, no timeout).
        """
        self.__log = log
        self.__host = host
        self.__login = login
        self.__password = password
        self.__port = port
        self.__timeout = timeout
        self.__client = None

    def __connect_before(self) -> Any:
        """
        Initialize the FTP client if not already connected.

        Raises:
            ConnectionError: If connection or authentication fails.
        """
        if self.__client is None:
            self.__log.debug('Init ftputil.FTPHost')
            try:
                self.__client = ftputil.FTPHost(
                    self.__host,
                    self.__login,
                    self.__password,
                    port=int(self.__port),
                    timeout=self.__normalize_timeout(),
                    session_factory=FtpSession,
                )
            except (ftputil.error.FTPError, ftplib.Error, OSError, EOFError, ValueError) as exc:
                raise ConnectionError(
                    f"{str(exc)}\nFailed to establish a connection. "
                    "Ensure the host, port, login and password are correct."
                )

        return self.__client

    def __normalize_timeout(self) -> float | None:
        """
        Convert the configured timeout into a socket-compatible value.
        """
        if self.__timeout is False or self.__timeout is None:
            return None

        if isinstance(self.__timeout, str):
            timeout = self.__timeout.strip()
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
        client = self.__connect_before()
        client.upload(local_path, remote_path)

    def get(self, remote_path: str, local_path: str) -> None:
        """
        Download a remote file from the FTP server.

        Args:
            remote_path (str): Path of the remote file.
            local_path (str): Destination path on the local host.
        """
        client = self.__connect_before()
        client.download(remote_path, local_path)

    def stat(self, filepath: str) -> Any:
        """
        Retrieve metadata for a remote file.

        Args:
            filepath (str): Remote file path.

        Returns:
            Any: Object with attributes similar to Python's os.stat.
        """
        client = self.__connect_before()
        return client.stat(filepath)

    def chdir(self, path: str | None = None) -> None:
        """
        Change the current working directory of the FTP session.

        Args:
            path (Optional[str]): Target directory. If None, no change occurs.
        """
        client = self.__connect_before()
        if path is not None:
            client.chdir(path)

    def chmod(self, path: str, mode: int) -> None:
        """
        Change the mode (permissions) of a remote file.

        Args:
            path (str): Path of the file.
            mode (int): Unix-style permissions (like os.chmod).
        """
        client = self.__connect_before()
        client.chmod(path, mode)

    def rename(self, old_path: str, new_path: str) -> None:
        """
        Rename a file or directory on the remote server.

        Args:
            old_path (str): Existing path.
            new_path (str): New path.
        """
        client = self.__connect_before()
        client.rename(old_path, new_path)

    def walk(self, remote_path: str) -> Generator[Tuple[str, List[str], List[str]], None, None]:
        """
        Walk through remote directories, yielding paths, folders, and files.

        Args:
            remote_path (str): Remote directory to traverse.

        Yields:
            Tuple[str, List[str], List[str]]: (current_path, folders, files)
        """
        client = self.__connect_before()
        walk_path = remote_path if remote_path != "" else client.curdir
        for path, folders, files in client.walk(walk_path):
            if remote_path == "":
                path = self.__remove_current_directory_prefix(client, path)
            yield path, folders, files

    @staticmethod
    def __remove_current_directory_prefix(client: Any, path: str) -> str:
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
        if self.__client is not None:
            self.__log.debug('Close ftputil.FTPHost client')
            self.__client.close()
            self.__client = None
