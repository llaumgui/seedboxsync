# Generated from a schema diff on 2026-09-12 10:23.
# ruff: noqa: ANN001, ANN201, D100, D103, F403, F405
# type: ignore
from peewee import *


def up(migrator, db):
    class TaskStatus(Model):
        key = CharField(primary_key=True)
        running = BooleanField(default=False)
        started = DateTimeField(null=True)
        finished = DateTimeField(null=True)

        class Meta:
            database = db
            table_name = "taskstatus"

    db.create_tables([TaskStatus])
    migrator.migrate(migrator.drop_table("lock", safe=True))


def down(migrator, db):
    migrator.migrate(migrator.drop_table("taskstatus"))
