# Generated from a schema diff on 2026-09-25 22:07.
# ruff: noqa: ANN001, ANN201, D100, D103, F403
# type: ignore
from flask import current_app
from peewee import *
from seedboxsync.core.database.models import Torrent


def up(migrator, db):
    with current_app.app_context():
        torrents = Torrent.select().where((Torrent.source == "") | (Torrent.source.is_null()))
        for torrent in torrents:
            torrent.source = torrent.announcer
            torrent.save()
