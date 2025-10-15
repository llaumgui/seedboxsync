# -*- coding: utf-8 -*-
#
# Copyright (C) 2015-2025 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
from peewee import CharField, TextField
from seedboxsync import __version__ as version
from seedboxsync.core.dao import SeedboxSyncModel


class SeedboxSync(SeedboxSyncModel):
    """
    Data Access Object (DAO) for application metadata and internal configuration.

    This table stores key–value pairs used for SeedboxSync's internal state
    management and configuration, such as locks, versioning, or runtime
    parameters.

    Attributes:
        key (str): Unique identifier for the configuration entry.
        value (str): Stored value associated with the key.
    """

    key = CharField(primary_key=True)
    value = TextField()

    @staticmethod
    def get_db_version() -> str:
        """
        Return database model version.

        Returns:
            str: The database model version.
        """
        return str(SeedboxSync.select(SeedboxSync.value).where(SeedboxSync.key == 'db_version').first().value)  # Use old style to prevent Peewee 2 databases.

    @staticmethod
    def set_db_version(db_version: str) -> None:
        """
        Upsert database model version.

        Args:
            db_version (str): The database model version.
        """
        SeedboxSync.replace(key='db_version', value=db_version).execute()

    @staticmethod
    def get_version() -> str:
        """
        Get SeedboxSync version.

        Returns:
            str: The database model version.
        """
        return str(SeedboxSync.get(SeedboxSync.key == 'version').value)

    @staticmethod
    def set_version() -> None:
        """
        Upsert SeedboxSync version.
        """
        SeedboxSync.replace(key='version', value=version).execute()
