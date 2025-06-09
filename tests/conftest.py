"""
PyTest Fixtures.
"""

import pytest
from cement import fs
from unittest import mock
from unittest.mock import patch


@pytest.fixture(scope="function")
def tmp(request):
    """
    Create a `tmp` object that geneates a unique temporary directory, and file
    for each test function that requires it.
    """
    t = fs.Tmp()
    yield t
    t.remove()


@pytest.fixture
def mock_sftp(monkeypatch):
    mock_transport = mock.MagicMock()
    mock_sftp = mock.MagicMock()

    monkeypatch.setattr('paramiko.Transport', lambda *a, **kw: mock_transport)
    monkeypatch.setattr('paramiko.SFTPClient.from_transport', lambda *a, **kw: mock_sftp)

    return mock_sftp


@pytest.fixture
def mock_empty_download():
    with patch('seedboxsync.core.sync.sftp_client.SftpClient.walk', return_value=[]):
        yield
