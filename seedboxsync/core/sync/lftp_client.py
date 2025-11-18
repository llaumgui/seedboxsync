# -*- coding: utf-8 -*-
#
# Copyright (C) 2015-2025 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
"""
Transport client using LFTP with parallel download support.
"""
import os
import subprocess
import shlex
from typing import Generator, Tuple, List, Optional
from cement.core.log import LogInterface
from seedboxsync.core.sync.abstract_client import AbstractClient
from seedboxsync.core.sync.sync import ConnectionError


class LftpStatResult:
    """
    Mock stat result object compatible with paramiko.SFTPAttributes.

    Provides file metadata in a format compatible with the AbstractClient interface.
    """
    def __init__(self, st_mode: int = 0, st_size: int = 0, st_uid: int = 0,
                 st_gid: int = 0, st_atime: int = 0, st_mtime: int = 0):
        self.st_mode = st_mode
        self.st_size = st_size
        self.st_uid = st_uid
        self.st_gid = st_gid
        self.st_atime = st_atime
        self.st_mtime = st_mtime


class LftpClient(AbstractClient):
    """
    LFTP transport client with parallel download support.

    Handles file transfers using LFTP's advanced features including parallel
    segmented downloads (pget), mirror operations, and multi-protocol support.
    Supports FTP, FTPS, SFTP, HTTP, HTTPS, and more.
    """
    __log: LogInterface
    __host: str
    __login: str
    __password: str
    __port: str
    __timeout: str | bool
    __protocol: str
    __pget_segments: int
    __max_retries: int
    __cwd: str

    def __init__(self, log: LogInterface, host: str, login: str, password: str,
                 port: str = "22", timeout: str | bool = False,
                 protocol: str = "sftp", pget_segments: int = 5,
                 max_retries: int = 3):
        """
        Initialize the LFTP client with connection parameters.

        Args:
            log (LogInterface): Logger instance.
            host (str): Remote server hostname.
            login (str): Username for authentication.
            password (str): Password for authentication.
            port (str): Server port (default: '22' for SFTP).
            timeout (str | bool): Network timeout in seconds (default: False, no timeout).
            protocol (str): Protocol to use (sftp, ftp, ftps, etc.). Default: 'sftp'.
            pget_segments (int): Number of parallel segments for pget. Default: 5.
            max_retries (int): Maximum number of retries for failed operations. Default: 3.
        """
        self.__log = log
        self.__host = host
        self.__login = login
        self.__password = password
        self.__port = port
        self.__timeout = timeout if timeout else "30"
        self.__protocol = protocol
        self.__pget_segments = pget_segments
        self.__max_retries = max_retries
        self.__cwd = "/"

        # Test connection
        self.__test_connection()

    def __test_connection(self) -> None:
        """
        Test the LFTP connection and verify credentials.

        Raises:
            ConnectionError: If connection or authentication fails.
        """
        try:
            result = self.__run_lftp_command("pwd")
            if result.returncode != 0:
                raise ConnectionError(f'LFTP connection test failed: {result.stderr}')
            self.__log.debug('LFTP connection test successful')
        except Exception as exc:
            raise ConnectionError(f'Failed to connect via LFTP: {str(exc)}')

    def __get_connection_url(self) -> str:
        """
        Build the LFTP connection URL.

        Returns:
            str: Connection URL in format: protocol://user:password@host:port
        """
        # Escape special characters in password for URL
        password_escaped = self.__password.replace('@', '%40').replace(':', '%3A')
        return f"{self.__protocol}://{self.__login}:{password_escaped}@{self.__host}:{self.__port}"

    def __run_lftp_command(self, command: str, input_data: Optional[str] = None) -> subprocess.CompletedProcess[str]:
        """
        Execute an LFTP command.

        Args:
            command (str): LFTP command to execute.
            input_data (Optional[str]): Additional commands to pass via stdin.

        Returns:
            subprocess.CompletedProcess: Result of the command execution.
        """
        url = self.__get_connection_url()

        # Build LFTP script
        script_lines = [
            f"set net:timeout {self.__timeout}",
            f"set net:max-retries {self.__max_retries}",
            "set net:reconnect-interval-base 5",
            "set net:reconnect-interval-multiplier 1",
            "set ssl:verify-certificate no",  # For testing; should be configurable in production
        ]

        if self.__cwd != "/":
            script_lines.append(f"cd {shlex.quote(self.__cwd)}")

        script_lines.append(command)

        if input_data:
            script_lines.append(input_data)

        script = "; ".join(script_lines)

        self.__log.debug(f'Running LFTP command: {command}')

        try:
            result = subprocess.run(
                ["lftp", "-c", f"open {url} && {script}"],
                capture_output=True,
                text=True,
                timeout=int(self.__timeout) * 3 if self.__timeout else None
            )
            return result
        except subprocess.TimeoutExpired:
            self.__log.error(f'LFTP command timed out: {command}')
            raise
        except FileNotFoundError:
            raise ConnectionError("LFTP executable not found. Please install LFTP: apt-get install lftp or brew install lftp")

    def put(self, local_path: str, remote_path: str) -> None:
        """
        Upload a local file to the remote server.

        Args:
            local_path (str): Path to the local file.
            remote_path (str): Destination path on the server (including filename).
        """
        self.__log.debug(f'Uploading {local_path} to {remote_path}')

        # Ensure the remote directory exists
        remote_dir = os.path.dirname(remote_path)
        if remote_dir:
            self.__run_lftp_command(f"mkdir -p -f {shlex.quote(remote_dir)}")

        # Upload file
        result = self.__run_lftp_command(f"put {shlex.quote(local_path)} -o {shlex.quote(remote_path)}")

        if result.returncode != 0:
            raise IOError(f'Failed to upload {local_path}: {result.stderr}')

    def get(self, remote_path: str, local_path: str) -> None:
        """
        Download a remote file using parallel segmented transfer (pget).

        Args:
            remote_path (str): Path of the remote file.
            local_path (str): Destination path on the local host.
        """
        self.__log.debug(f'Downloading {remote_path} to {local_path} with {self.__pget_segments} segments')

        # Ensure local directory exists
        local_dir = os.path.dirname(local_path)
        if local_dir:
            os.makedirs(local_dir, exist_ok=True)

        # Use pget for parallel segmented download
        result = self.__run_lftp_command(
            f"pget -n {self.__pget_segments} {shlex.quote(remote_path)} -o {shlex.quote(local_path)}"
        )

        if result.returncode != 0:
            raise IOError(f'Failed to download {remote_path}: {result.stderr}')

    def stat(self, filepath: str) -> LftpStatResult:
        """
        Retrieve metadata for a remote file.

        Args:
            filepath (str): Remote file path.

        Returns:
            LftpStatResult: Object with attributes similar to Python's os.stat.
        """
        self.__log.debug(f'Getting stat for {filepath}')

        # Use cls -l command to get file information
        result = self.__run_lftp_command(f"cls -l {shlex.quote(filepath)}")

        if result.returncode != 0:
            raise FileNotFoundError(f'File not found: {filepath}')

        # Parse ls -l output to extract size
        # Format: -rw-r--r--   1 user group    12345 Jan 01 12:00 filename
        output = result.stdout.strip()
        if not output:
            raise FileNotFoundError(f'File not found: {filepath}')

        parts = output.split()
        if len(parts) < 5:
            raise IOError(f'Unable to parse stat output for {filepath}')

        try:
            # The size is typically the 5th field (index 4)
            size = int(parts[4])
        except (ValueError, IndexError):
            # Try alternative parsing
            size = 0
            for part in parts:
                try:
                    size = int(part)
                    break
                except ValueError:
                    continue

        return LftpStatResult(st_size=size)

    def chdir(self, path: str | None = None) -> None:
        """
        Change the current working directory.

        Args:
            path (Optional[str]): Target directory. If None, no change occurs.
        """
        if path is not None:
            self.__log.debug(f'Changing directory to {path}')
            result = self.__run_lftp_command(f"cd {shlex.quote(path)}")

            if result.returncode != 0:
                raise IOError(f'Failed to change directory to {path}: {result.stderr}')

            self.__cwd = path

    def chmod(self, path: str, mode: int) -> None:
        """
        Change the mode (permissions) of a remote file.

        Args:
            path (str): Path of the file.
            mode (int): Unix-style permissions (octal, like os.chmod).
        """
        self.__log.debug(f'Setting permissions {oct(mode)} on {path}')

        # Convert integer mode to octal string
        mode_octal = oct(mode)[2:]  # Remove '0o' prefix

        result = self.__run_lftp_command(f"chmod {mode_octal} {shlex.quote(path)}")

        if result.returncode != 0:
            raise IOError(f'Failed to chmod {path}: {result.stderr}')

    def rename(self, old_path: str, new_path: str) -> None:
        """
        Rename a file or directory on the remote server.

        Args:
            old_path (str): Existing path.
            new_path (str): New path.
        """
        self.__log.debug(f'Renaming {old_path} to {new_path}')

        result = self.__run_lftp_command(f"mv {shlex.quote(old_path)} {shlex.quote(new_path)}")

        if result.returncode != 0:
            raise IOError(f'Failed to rename {old_path} to {new_path}: {result.stderr}')

    def walk(self, remote_path: str) -> Generator[Tuple[str, List[str], List[str]], None, None]:
        """
        Walk through remote directories, yielding paths, folders, and files.

        Args:
            remote_path (str): Remote directory to traverse.

        Yields:
            Tuple[str, List[str], List[str]]: (current_path, folders, files)

        Note:
            Uses LFTP's glob command with -d (directories) and -f (files) flags.
        """
        full_path = os.path.join(self.__cwd, remote_path) if remote_path else self.__cwd

        # Use glob to get directories and files separately
        dirs_result = self.__run_lftp_command(f"cd {shlex.quote(full_path)} && glob -d *")
        files_result = self.__run_lftp_command(f"cd {shlex.quote(full_path)} && glob -f *")

        if dirs_result.returncode != 0:
            raise IOError(f'Failed to list directory {remote_path}: {dirs_result.stderr}')

        # Parse output - glob returns one filename per line
        folders = [line.strip() for line in dirs_result.stdout.strip().split('\n') if line.strip()]
        files = [line.strip() for line in files_result.stdout.strip().split('\n') if line.strip()]

        yield remote_path, folders, files

        # Recursively walk subdirectories
        for folder in folders:
            new_path = os.path.join(remote_path, folder) if remote_path else folder
            for x in self.walk(new_path):
                yield x

    def close(self) -> None:
        """
        Close the LFTP connection.

        Note: LFTP runs as individual commands, so there's no persistent connection to close.
        """
        self.__log.debug('Closing LFTP client (no persistent connection)')
        # LFTP doesn't maintain a persistent connection in this implementation
        pass
