# Generated from a schema diff on 2026-10-11 10:56.
# ruff: noqa: ANN001, ANN201, D100, D103, F403, F405
# type: ignore
from flask import current_app
from peewee import *
from seedboxsync.core.database.models import User


def up(migrator, db):
    migrator.migrate(migrator.add_column("user", "is_admin", BooleanField(default=False)))

    # Pass all old users as admin
    with current_app.app_context():
        users = User.select()
        for user in users:
            user.is_admin = True
            user.save()


def down(migrator, db):
    migrator.migrate(migrator.drop_column("user", "is_admin"))
