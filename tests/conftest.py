#
# Copyright (C) 2025-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
import shutil
from unittest.mock import MagicMock, patch
import pytest
from seedboxsync import create_app


@pytest.fixture
def app(tmp_path):
    """Create an application backed by an isolated copy of the test database."""
    database = tmp_path / "seedboxsync.db"
    shutil.copy("tests/resources/seedboxsync.db", database)

    app = create_app(
        {
            "TESTING": True,
            "DATABASE": str(database),
            "SECRET_KEY": "pytest",
            "CACHE_TYPE": "NullCache",
            "BABEL_DEFAULT_LOCALE": "en",
        }
    )

    # FlaskDB opens the database while initializing and migrating it. Close
    # that connection so request and CLI contexts can manage their own.
    db = app.extensions["flaskdb"].database
    if not db.is_closed():
        db.close()

    yield app

    huey = app.extensions.get("huey")
    if huey is not None:
        huey.storage.close()

    if not db.is_closed():
        db.close()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()


@pytest.fixture
def mock_urllib():
    """Prevent Healthchecks tests from issuing HTTP requests."""
    with patch("seedboxsync.core.ping.client.healthchecks.urllib.request.urlopen") as mock_urlopen:
        mock_urlopen.return_value = MagicMock()
        yield mock_urlopen
