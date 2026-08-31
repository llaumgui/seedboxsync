#
# Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
"""Peewee DAO model for User."""

import datetime
from typing import Self
from flask_login import UserMixin
from peewee import AutoField, CharField, DateTimeField
from werkzeug.security import check_password_hash
from seedboxsync.core.dao import SeedboxSyncModel


class User(SeedboxSyncModel, UserMixin):  # type: ignore[misc]
    """
    Data Access Object (DAO) representing a user.

    This model stores user account information, including authentication
    credentials, email address, account creation date, and last login timestamp.

    Attributes:
        id (int): Auto-incremented primary key.
        username (str): Unique username of the user.
        password (str): Hashed password of the user.
        email (str): Unique email address of the user.
        created (datetime): Timestamp when the user account was created.
        last_login (datetime): Timestamp when the user last logged in.
    """

    id = AutoField(help_text="Unique identifier of the user")
    username = CharField(unique=True, help_text="Username of the user")
    password = CharField(help_text="Salted password of the user")
    email = CharField(unique=True, help_text="Email address of the user")
    created = DateTimeField(default=datetime.datetime.now, help_text="Timestamp when the user was created")
    last_login = DateTimeField(default=datetime.datetime.now, help_text="Timestamp when the user last logged in")

    @classmethod
    def authenticate(cls, login: str, password: str) -> Self | None:
        """
        Authenticate a user using their username or email address.

        Args:
            login (str): Username or email address.
            password (str): Plain-text password to verify.

        Returns:
            Self | None: The authenticated user, or None if authentication fails.
        """
        user = cls.get_or_none((cls.username == login) | (cls.email == login))

        if user is None:
            return None

        if not check_password_hash(user.password, password):
            return None

        return user
