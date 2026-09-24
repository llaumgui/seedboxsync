# Generated from a schema diff on 2026-09-24 07:59.
# ruff: noqa: ANN001, ANN201, D100, D103, F403, F405
# type: ignore
from flask import current_app as app
from peewee import *
from seedboxsync.core.database.models import Torrent


def up(migrator, db):
    migrator.migrate(migrator.add_column("torrent", "announcer", TextField(null=True)))
    migrator.migrate(migrator.add_column("torrent", "source", TextField(null=True)))
    migrator.migrate(migrator.add_column("torrent", "total_files", IntegerField(null=True)))
    migrator.migrate(migrator.add_column("torrent", "total_size", IntegerField(null=True)))
    migrator.migrate(migrator.add_column("torrent", "private", BooleanField(default=False)))

    # Update database
    with app.app_context():
        torrents = Torrent.select().where((Torrent.announcer == "") | (Torrent.announcer.is_null()))
        for torrent in torrents:
            torrent.save()


def down(migrator, db):
    migrator.migrate(migrator.drop_column("torrent", "private"))
    migrator.migrate(migrator.drop_column("torrent", "total_size"))
    migrator.migrate(migrator.drop_column("torrent", "total_files"))
    migrator.migrate(migrator.drop_column("torrent", "source"))
    migrator.migrate(migrator.drop_column("torrent", "announcer"))
