# -*- coding: utf-8 -*-
#
# Copyright (C) 2015-2025 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
"""
Tests for LFTP client.
"""
import pytest
from unittest import mock
from cement import TestApp
from seedboxsync.core.sync.lftp_client import LftpClient, LftpStatResult
from seedboxsync.core.sync.sync import ConnectionError


class TestLftpStatResult:
    """Tests for LftpStatResult class."""

    def test_lftp_stat_result_creation(self):
        """Test creating LftpStatResult with default values."""
        stat = LftpStatResult()
        assert stat.st_mode == 0
        assert stat.st_size == 0
        assert stat.st_uid == 0
        assert stat.st_gid == 0
        assert stat.st_atime == 0
        assert stat.st_mtime == 0

    def test_lftp_stat_result_with_values(self):
        """Test creating LftpStatResult with custom values."""
        stat = LftpStatResult(
            st_mode=33188,
            st_size=1024,
            st_uid=1000,
            st_gid=1000,
            st_atime=1234567890,
            st_mtime=1234567890
        )
        assert stat.st_mode == 33188
        assert stat.st_size == 1024
        assert stat.st_uid == 1000
        assert stat.st_gid == 1000
        assert stat.st_atime == 1234567890
        assert stat.st_mtime == 1234567890


class TestLftpClient:
    """Tests for LftpClient class."""

    @pytest.fixture
    def mock_subprocess(self, monkeypatch):
        """Mock subprocess.run for testing."""
        mock_result = mock.MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "/"
        mock_result.stderr = ""

        def mock_run(*args, **kwargs):
            return mock_result

        monkeypatch.setattr('subprocess.run', mock_run)
        return mock_result

    @pytest.fixture
    def lftp_client(self, mock_subprocess):
        """Create an LFTP client instance for testing."""
        with TestApp() as app:
            app.setup()
            client = LftpClient(
                log=app.log,
                host="test.example.com",
                login="testuser",
                password="testpass",
                port="22",
                timeout="30"
            )
            return client

    def test_lftp_client_initialization(self, lftp_client):
        """Test LFTP client initialization."""
        assert lftp_client._LftpClient__host == "test.example.com"
        assert lftp_client._LftpClient__login == "testuser"
        assert lftp_client._LftpClient__password == "testpass"
        assert lftp_client._LftpClient__port == "22"
        assert lftp_client._LftpClient__timeout == "30"

    def test_connection_url_generation(self, lftp_client):
        """Test connection URL generation."""
        url = lftp_client._LftpClient__get_connection_url()
        assert url == "sftp://testuser:testpass@test.example.com:22"

    def test_connection_url_with_special_chars(self, mock_subprocess):
        """Test connection URL generation with special characters in password."""
        with TestApp() as app:
            app.setup()
            client = LftpClient(
                log=app.log,
                host="test.example.com",
                login="user@domain",
                password="pass:word@123",
                port="22"
            )
            url = client._LftpClient__get_connection_url()
            assert url == "sftp://user@domain:pass%3Aword%40123@test.example.com:22"

    def test_get_method(self, lftp_client, mock_subprocess, tmp_path):
        """Test file download using get method."""
        mock_subprocess.stdout = ""
        local_file = tmp_path / "file.txt"
        lftp_client.get("/remote/file.txt", str(local_file))
        # Verify that subprocess.run was called (implicitly tested by not raising an error)

    def test_put_method(self, lftp_client, mock_subprocess):
        """Test file upload using put method."""
        mock_subprocess.stdout = ""
        lftp_client.put("/local/file.txt", "/remote/file.txt")
        # Verify that subprocess.run was called (implicitly tested by not raising an error)

    def test_stat_method(self, lftp_client, mock_subprocess):
        """Test stat method to retrieve file metadata."""
        mock_subprocess.stdout = "-rw-r--r--   1 user group    1024 Jan 01 12:00 file.txt"
        stat_result = lftp_client.stat("/remote/file.txt")
        assert isinstance(stat_result, LftpStatResult)
        assert stat_result.st_size == 1024

    def test_stat_method_file_not_found(self, lftp_client, mock_subprocess):
        """Test stat method when file is not found."""
        mock_subprocess.returncode = 1
        mock_subprocess.stdout = ""
        with pytest.raises(FileNotFoundError):
            lftp_client.stat("/remote/nonexistent.txt")

    def test_chdir_method(self, lftp_client, mock_subprocess):
        """Test changing directory."""
        mock_subprocess.stdout = ""
        lftp_client.chdir("/remote/path")
        assert lftp_client._LftpClient__cwd == "/remote/path"

    def test_chdir_with_none(self, lftp_client, mock_subprocess):
        """Test chdir with None (should not change directory)."""
        original_cwd = lftp_client._LftpClient__cwd
        lftp_client.chdir(None)
        assert lftp_client._LftpClient__cwd == original_cwd

    def test_chmod_method(self, lftp_client, mock_subprocess):
        """Test changing file permissions."""
        mock_subprocess.stdout = ""
        lftp_client.chmod("/remote/file.txt", 0o644)
        # Verify that subprocess.run was called (implicitly tested by not raising an error)

    def test_rename_method(self, lftp_client, mock_subprocess):
        """Test renaming a file."""
        mock_subprocess.stdout = ""
        lftp_client.rename("/remote/old.txt", "/remote/new.txt")
        # Verify that subprocess.run was called (implicitly tested by not raising an error)

    def test_walk_method(self, lftp_client, monkeypatch):
        """Test walking through directories."""
        def mock_run_walk(*args, **kwargs):
            result = mock.MagicMock()
            result.returncode = 0

            # Check which command is being run
            cmd = args[0][2] if len(args) > 0 and len(args[0]) > 2 else ""

            # Determine if we're in root or subdirectory by checking the path in cmd
            if '/remote/subdir' in cmd or 'subdir' in cmd.split('&&')[-1]:
                # We're in the subdirectory - return empty
                result.stdout = ""
            elif 'glob -d' in cmd:
                # Root directory, return subdirectory
                result.stdout = "subdir\n"
            elif 'glob -f' in cmd:
                # Root directory, return files
                result.stdout = "file1.txt\nfile2.txt\n"
            else:
                result.stdout = "/"

            return result

        monkeypatch.setattr('subprocess.run', mock_run_walk)

        results = list(lftp_client.walk("/remote"))
        assert len(results) >= 1
        path, folders, files = results[0]
        assert path == "/remote"
        assert "subdir" in folders
        assert "file1.txt" in files
        assert "file2.txt" in files

    def test_close_method(self, lftp_client):
        """Test closing the client."""
        # Should not raise any errors
        lftp_client.close()

    def test_connection_failure(self, monkeypatch):
        """Test connection failure handling."""
        def mock_run_fail(*args, **kwargs):
            result = mock.MagicMock()
            result.returncode = 1
            result.stdout = ""
            result.stderr = "Connection failed"
            return result

        monkeypatch.setattr('subprocess.run', mock_run_fail)

        with TestApp() as app:
            app.setup()
            # ConnectionError calls sys.exit(), so we expect SystemExit
            with pytest.raises(SystemExit):
                LftpClient(
                    log=app.log,
                    host="invalid.example.com",
                    login="testuser",
                    password="testpass",
                    port="22"
                )

    def test_lftp_not_installed(self, monkeypatch):
        """Test handling when LFTP is not installed."""
        def mock_run_not_found(*args, **kwargs):
            raise FileNotFoundError("lftp command not found")

        monkeypatch.setattr('subprocess.run', mock_run_not_found)

        with TestApp() as app:
            app.setup()
            # ConnectionError calls sys.exit(), so we expect SystemExit
            with pytest.raises(SystemExit) as excinfo:
                LftpClient(
                    log=app.log,
                    host="test.example.com",
                    login="testuser",
                    password="testpass",
                    port="22"
                )
            assert "LFTP executable not found" in str(excinfo.value)
