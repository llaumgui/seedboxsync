# -*- coding: utf-8 -*-
#
# Copyright (C) 2025-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
"""
A module to manage SeedboxSync configuration from Database or environment variables.
"""

from flask import Flask
from typing import Any
from seedboxsync.core.dao import typed_peewee_dicts, SeedboxSync


class Config(object):
    """
    Config.
    """

    DB_CONFIG_PREFIX = "config_"
    CONFIG_NAMESPACE = "SEEDBOXSYNC_"
    DEFAULT_CONFIG: dict[str, Any] = {
        CONFIG_NAMESPACE + "SYNC_BLACKHOLE_ENABLED": False,
        CONFIG_NAMESPACE + "SYNC_SEEDBOX_ENABLED": False,
        CONFIG_NAMESPACE + "SEEDBOX_HOST": "my-seedbox.ltd",
        CONFIG_NAMESPACE + "SEEDBOX_PORT": "22",
        CONFIG_NAMESPACE + "SEEDBOX_LOGIN": "me",
        CONFIG_NAMESPACE + "SEEDBOX_PASSWORD": "p4sw0rd",
        CONFIG_NAMESPACE + "SEEDBOX_TIMEOUT": False,
        CONFIG_NAMESPACE + "SEEDBOX_PROTOCOL": "sftp",
        CONFIG_NAMESPACE + "SEEDBOX_MAX_CONCURRENT_PREFETCH_REQUESTS": "128",
        CONFIG_NAMESPACE + "SEEDBOX_CHMOD": False,
        CONFIG_NAMESPACE + "SEEDBOX_TMP_PATH": "./tmp",
        CONFIG_NAMESPACE + "SEEDBOX_WATCH_PATH": "./watch",
        CONFIG_NAMESPACE + "SEEDBOX_FINISHED_PATH": "./files",
        CONFIG_NAMESPACE + "SEEDBOX_PREFIXED_PATH": "/files",
        CONFIG_NAMESPACE + "SEEDBOX_PART_SUFFIX": ".part",
        CONFIG_NAMESPACE + "SEEDBOX_EXCLUDE_SYNCING": "",
        CONFIG_NAMESPACE + "LOCAL_WATCH_PATH": "~/watch",
        CONFIG_NAMESPACE + "LOCAL_DOWNLOAD_PATH": "~/Download/",
        CONFIG_NAMESPACE + "HEALTHCHECKS_SYNC_SEEDBOX_ENABLED": False,
        CONFIG_NAMESPACE + "HEALTHCHECKS_SYNC_SEEDBOX_PING_URL": "",
        CONFIG_NAMESPACE + "HEALTHCHECKS_SYNC_BLACKHOLE_ENABLED": False,
        CONFIG_NAMESPACE + "HEALTHCHECKS_SYNC_BLACKHOLE_PING_URL": "",
    }

    def __init__(self, app: Flask, test_config: dict[str, str] | None = None):
        """
        Initialize a new Config instance.

        Args:
            app (Flask): The Flask application to configure.
            test_config (dict[str, str] | None): Configuration for testing.
        """

        self.app = app
        self.app.config.from_prefixed_env()  # Set from env prefixed by 'FLASK_'

        # Load config from database
        db_config = self._load_config_from_database()
        self.app.config.from_mapping(db_config)

        self._check_config()  # Do all checks

        self.app.config.setdefault("CACHE_TYPE", "SimpleCache")  # Init Flask Cache
        self.app.config.setdefault("SWAGGER_UI_DOC_EXPANSION", "list")  # Expense swager namespaces
        self.app.config.setdefault("PROPAGATE_EXCEPTIONS", False)

    def _check_config(self) -> None:
        """Check all configurations needed."""
        # SECRET_KEY warning
        if self.app.config.get("SECRET_KEY") is None and self.app.config["TESTING"] is None:
            self.app.logger.warning("Warning: SECRET_KEY is still not set. Set it in production to secure your sessions.")

    def _load_config_from_database(self) -> dict[str, str]:
        """Load application configuration from the database."""

        config = Config.DEFAULT_CONFIG.copy()

        db_config = typed_peewee_dicts(
            SeedboxSync.select(
                SeedboxSync.key,
                SeedboxSync.value,
            )
            .where(SeedboxSync.key.startswith(Config.DB_CONFIG_PREFIX))
            .dicts()
        )

        for conf in db_config:
            config_key = Config.CONFIG_NAMESPACE + conf["key"].removeprefix("config_").upper()
            value = self._convert_config_value(config_key, conf["value"])
            display_value = "*****" if "PASSWORD" in config_key.upper() else value

            self.app.logger.debug(f"Loading config from database: {config_key} = {display_value}")
            if config_key not in Config.DEFAULT_CONFIG:
                self.app.logger.warning("Ignoring unknown configuration key: %s", conf["key"])
                continue
            config[config_key] = value

        return config

    def _convert_config_value(self, config_key: str, value: Any) -> Any:
        """
        Convert a raw database configuration value to its expected Python type.

        Boolean options whose names end with ``_ENABLED`` are converted to
        ``True`` or ``False``. ``SEEDBOX_TIMEOUT`` is converted to an integer
        when defined, otherwise to ``False``. ``SEEDBOX_CHMOD`` is converted
        from an octal string to an integer when defined, otherwise to ``False``.

        All other values are returned unchanged.

        Args:
            config_key: Full Flask configuration key.
            value: Raw value loaded from the database.

        Returns:
            Any: The converted configuration value.
        """
        normalized_key = config_key.upper()
        raw_value = str(value or "").strip()

        if normalized_key.endswith("_ENABLED"):
            return raw_value.lower() not in {
                "",
                "0",
            }

        if normalized_key.endswith("SEEDBOX_TIMEOUT"):
            if not raw_value:
                return False
            timeout = int(raw_value)
            return timeout if timeout > 0 else False

        if normalized_key.endswith("SEEDBOX_CHMOD"):
            if not raw_value:
                return False
            return raw_value if raw_value not in ["", "0"] else False

        return value
