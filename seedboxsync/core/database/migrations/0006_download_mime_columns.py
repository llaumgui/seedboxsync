# Generated from a schema diff on 2026-09-13 12:15.
# ruff: noqa: ANN001, ANN201, D100, D103, F403, F405
# type: ignore
from flask import current_app as app
from peewee import *
from seedboxsync.core.database.models import Download


def up(migrator, db):
    migrator.migrate(migrator.add_column("download", "mime_extension", CharField(default="")))
    migrator.migrate(migrator.add_column("download", "mime_type", CharField(max_length=100, default="")))
    migrator.migrate(migrator.add_column("download", "mime_confidence", CharField(max_length=65, default="")))

    # Update database
    with app.app_context():
        downloads = Download.select().where((Download.mime_extension == "") | (Download.mime_extension.is_null()))
        for download in downloads:
            download.set_mime(True)


def down(migrator, db):
    migrator.migrate(migrator.drop_column("download", "mime_confidence"))
    migrator.migrate(migrator.drop_column("download", "mime_type"))
    migrator.migrate(migrator.drop_column("download", "mime_extension"))
