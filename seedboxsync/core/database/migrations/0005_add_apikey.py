# Generated from a schema diff on 2026-09-12 10:24.
# ruff: noqa: ANN001, ANN201, D100, D103, F403, F405
# type: ignore
import datetime
from peewee import *


def up(migrator, db):
    class User(Model):
        class Meta:
            database = db
            table_name = "user"

    class ApiKey(Model):
        user = ForeignKeyField(User, on_delete="CASCADE")
        name = CharField(max_length=64)
        key_hash = CharField(unique=True)
        created = DateTimeField(default=datetime.datetime.now)
        last_used = DateTimeField(null=True)

        class Meta:
            database = db
            table_name = "apikey"

    db.create_tables([ApiKey])


def down(migrator, db):
    migrator.migrate(migrator.drop_table("apikey"))
