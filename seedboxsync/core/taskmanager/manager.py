# -*- coding: utf-8 -*-
#
# Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#

from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from flask import Flask
from huey import SqliteHuey


class Manager:
    """
    Manage the Huey task queue integration with Flask.

    The manager creates a Huey instance from the application configuration,
    stores it in the Flask extensions registry, and proxies Huey attributes
    through the manager instance.
    """

    HUEY_DB_NAME = "huey.db"
    HUEY_APP_NAME = "seedboxsync"

    def __init__(self, app: Flask | None = None) -> None:
        """
        Initialize the Huey manager.

        Args:
            app: Optional Flask application to initialize immediately.
        """
        self.app: Flask | None = None
        self.__instance: SqliteHuey | None = None

        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask) -> None:
        """
        Initialize the Huey manager for a Flask application.

        The created Huey instance is stored in the Flask extensions registry
        under the ``huey`` key.

        Args:
            app: Flask application to initialize.
        """
        self.app = app

        huey_instance = self.init_huey()
        app.extensions["huey"] = huey_instance
        self.__instance = huey_instance

    def init_huey(self) -> SqliteHuey:
        """
        Create and configure the Huey task queue instance.

        Returns:
            The configured SQLite-backed Huey instance.
        """
        return SqliteHuey(
            self.HUEY_APP_NAME,
            filename=str(self._get_huey_database()),
        )

    def __getattr__(self, name: str) -> Any:
        """
        Proxy unknown attributes to the underlying Huey instance.

        Args:
            name: Name of the requested attribute.

        Returns:
            The attribute exposed by the underlying Huey instance.

        Raises:
            RuntimeError: If the manager has not been initialized.
            AttributeError: If the Huey instance does not expose the requested
                attribute.
        """
        if self.__instance is None:
            raise RuntimeError("The Huey manager has not been initialized with a Flask application.")

        return getattr(self.__instance, name)

    def _get_huey_database(self) -> Path:
        """
        Build the Huey database path from the application database URL.

        The Huey database is created in the same directory as the main SQLite
        database configured through ``app.config["DATABASE"]``.

        For example, the following database URL:

        ``sqlite:////home/user/.config/seedboxsync/seedboxsync.db``

        produces:

        ``/home/user/.config/seedboxsync/huey.db``

        Returns:
            The path to the Huey SQLite database file.

        Raises:
            RuntimeError: If the manager has not been initialized with a Flask
                application.
            ValueError: If the configured database is not a file-based SQLite
                database.
        """
        if self.app is None:
            raise RuntimeError("The Huey manager has not been initialized with a Flask application.")

        database_url: str = self.app.config["DATABASE"]
        parsed_url = urlparse(database_url)

        clean_path = parsed_url.path
        if clean_path.startswith("//"):
            clean_path = clean_path[1:]

        if parsed_url.scheme != "sqlite":
            raise ValueError(f"Unsupported database scheme: {parsed_url.scheme or '<missing>'}")

        if not parsed_url.path:
            raise ValueError("The SQLite database URL does not contain a file path.")

        if parsed_url.path in {":memory:", "/:memory:"}:
            raise ValueError("An in-memory SQLite database cannot be used to derive " "the Huey database path.")

        database_path = Path(clean_path)
        huey_database_path = database_path.with_name(self.HUEY_DB_NAME)

        self.app.logger.debug(
            "Using Huey task queue database path: %s",
            huey_database_path,
        )

        return huey_database_path
