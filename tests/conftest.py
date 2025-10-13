"""
PyTest Fixtures.
"""

import pytest
import os
import shutil
import yaml
from cement import fs
from unittest import mock
from unittest.mock import patch, MagicMock


@pytest.fixture(scope="function")
def tmp(request):
    """
    Create a `tmp` object that geneates a unique temporary directory, and file
    for each test function that requires it.
    """
    t = fs.Tmp()

    # Copy database
    test_db = os.path.abspath("tests/resources/seedboxsync.db")
    tmp_db = os.path.join(t.dir, "seedboxsync.db")
    shutil.copy(test_db, tmp_db)

    # Copy watch
    test_watch = os.path.abspath("tests/resources/watch")
    tmp_watch = os.path.join(t.dir, "watch")
    shutil.copytree(test_watch, tmp_watch)

    # Edit config and copy in tmp
    test_conf = os.path.abspath("tests/resources/seedboxsync.yml")
    tmp_conf = os.path.join(t.dir, "seedboxsync.yml")
    shutil.copy(test_conf, tmp_conf)
    with open(tmp_conf, 'r') as f:
        cfg = yaml.safe_load(f)
    cfg['local']['db_file'] = tmp_db
    cfg['local']['watch_path'] = tmp_watch
    with open(tmp_conf, 'w') as f:
        yaml.safe_dump(cfg, f)

    yield t, [tmp_conf], tmp_db, tmp_watch

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


@pytest.fixture
def mock_urllib():
    """
    Fixture that patches urllib.request.urlopen
    and stores call arguments for later assertions.
    """
    with patch('seedboxsync.ext.ext_healthchecks.urllib.request.urlopen') as mock_urlopen:
        mock_urlopen.return_value = MagicMock()  # fake HTTPResponse
        yield mock_urlopen  # yield mock object for inspection after test
