# Generated from a schema diff on 2026-10-17 16:15.
# ruff: noqa: ANN001, ANN201, D100, D103, F403, F405
# type: ignore
import datetime
from peewee import *


def up(migrator, db):
    class Log(Model):
        level = CharField(max_length=20, default="")
        logger = CharField(default="")
        module = CharField(default="")
        message = TextField(default="")
        timestamp = DateTimeField(default=datetime.datetime.now)

        class Meta:
            database = db
            table_name = "log"

    db.create_tables([Log])


def down(migrator, db):
    migrator.migrate(migrator.drop_table("log"))
