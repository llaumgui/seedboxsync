#
# Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
"""Peewee DAO model for ApiKey."""

import datetime
import hashlib
import secrets
from typing import Self, cast
from peewee import AutoField, CharField, DateTimeField, ForeignKeyField
from seedboxsync.core.database.dao import SeedboxSyncModel, User


class ApiKey(SeedboxSyncModel):
    """
    Data Access Object (DAO) representing an API Key.

    Stores API key metadata and hashed secret values associated with a user
    account for programmatic access.

    Attributes:
        id (int): Auto-incremented primary key.
        user (User): Foreign key reference to the associated user account.
        name (str): Human-readable label describing the purpose of the key.
        key_hash (str): SHA-256 hash of the generated raw API key.
        created (datetime): Timestamp when the API key was created.
        last_used (datetime | None): Timestamp when the API key was last used.
    """

    KEY_PREFIX = "sbx_"

    id = AutoField(help_text="Unique identifier of the API key")
    user = ForeignKeyField(User, backref="api_keys", on_delete="CASCADE", help_text="Owner of the API key")
    name = CharField(max_length=64, help_text="Description or label for the API key")
    key_hash = CharField(unique=True, help_text="SHA-256 hash of the plain-text API key")
    created = DateTimeField(default=datetime.datetime.now, help_text="Timestamp when the key was created")
    last_used = DateTimeField(null=True, help_text="Timestamp when the key was last authenticated")

    @classmethod
    def generate(cls, user: User, name: str) -> tuple[Self, str]:
        """
        Generate a new API key for a user.

        Computes a cryptographically secure random token, hashes it for storage,
        and returns both the database model instance and the raw token.

        Args:
            user (User): User model instance owning the new key.
            name (str): Descriptive label for the key.

        Returns:
            tuple[Self, str]: A tuple containing (ApiKey instance, raw_api_key_str).
                The raw key string must be displayed to the user immediately,
                as it cannot be recovered later.
        """
        raw_key = f"{cls.KEY_PREFIX}{secrets.token_urlsafe(32)}"
        key_hash = hashlib.sha256(raw_key.encode("utf-8")).hexdigest()

        api_key = cls.create(
            user=user,
            name=name,
            key_hash=key_hash,
        )

        return api_key, raw_key

    @classmethod
    def authenticate(cls, raw_key: str) -> User | None:
        """
        Authenticate an incoming API key string.

        Hashes the incoming raw key and verifies if a matching active key exists
        in the database. Updates `last_used` on success.

        Args:
            raw_key (str): Plain-text API key provided in the HTTP header/request.

        Returns:
            User | None: The matching User instance,
                or None if authentication fails.
        """
        if not raw_key or not raw_key.startswith(cls.KEY_PREFIX):
            return None

        key_hash = hashlib.sha256(raw_key.encode("utf-8")).hexdigest()
        api_key = cls.select(cls, User).join(User).where(cls.key_hash == key_hash).first()

        if api_key is None:
            return None

        # Update last_used timestamp
        api_key.last_used = datetime.datetime.now()
        api_key.save()

        return cast(User, api_key.user)
