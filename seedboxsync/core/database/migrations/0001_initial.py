# Generated from a schema diff on 2026-09-12 10:16.
# ruff: noqa: ANN001, ANN201, D100, D103, F403, F405
# type: ignore
import datetime
from peewee import *


def up(migrator, db):
    class Download(Model):
        path = TextField()
        seedbox_size = IntegerField()
        local_size = IntegerField(default=0)
        started = DateTimeField(default=datetime.datetime.now)
        finished = DateTimeField(default=0)

        class Meta:
            database = db
            table_name = "download"

    db.create_tables([Download])

    class SeedboxSync(Model):
        key = CharField(primary_key=True)
        value = TextField()

        class Meta:
            database = db
            table_name = "seedboxsync"

    db.create_tables([SeedboxSync])

    class Torrent(Model):
        name = TextField()
        announce = TextField()
        sent = DateTimeField(default=datetime.datetime.now)

        class Meta:
            database = db
            table_name = "torrent"

    db.create_tables([Torrent])


def down(migrator, db):
    migrator.migrate(migrator.drop_table("torrent"))
    migrator.migrate(migrator.drop_table("seedboxsync"))
    migrator.migrate(migrator.drop_table("download"))
