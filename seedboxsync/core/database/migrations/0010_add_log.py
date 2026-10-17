# Generated from a schema diff on 2026-10-16 13:42.
# ruff: noqa: ANN001, ANN201, D100, D103, F403, F405
# type: ignore
import datetime
from peewee import *


def up(migrator, db):
    class Log(Model):
        level_name = CharField(max_length=20)
        logger_name = CharField()
        message = TextField()
        timestamp = DateTimeField(default=datetime.datetime.now)

        class Meta:
            database = db
            table_name = "log"

    db.create_tables([Log])


def down(migrator, db):
    migrator.migrate(migrator.drop_table("log"))
