# -*- coding: utf-8 -*-
#
# Copyright (C) 2025-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
import os
import pytest
import shutil
import tempfile
from seedboxsync import create_app


@pytest.fixture
def app():
    """
    Create app fixture
    """
    db_fd, tmp_db = tempfile.mkstemp()

    # Copy database
    test_db = os.path.abspath("tests/resources/seedboxsync.db")
    shutil.copy(test_db, tmp_db)

    app = create_app({
        'TESTING': True,
        'DATABASE': tmp_db,
        'SECRET_KEY': 'pytest',
        'CACHE_TYPE': 'NullCache',
        'BABEL_DEFAULT_LOCALE': 'en',
    })

    # Can close DB, reopen for test
    db_wrapper = app.extensions.get("flaskdb") or None
    if db_wrapper is not None:
        db = db_wrapper.database
        if not db.is_closed():
            db.close()

    yield app

    # Cleanup
    os.close(db_fd)
    os.unlink(tmp_db)


@pytest.fixture
def client(app):
    """
    Create client fixture
    """
    return app.test_client()


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()
