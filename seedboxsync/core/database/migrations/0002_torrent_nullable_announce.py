# Generated from a schema diff on 2026-09-12 10:18.
# ruff: noqa: ANN001, ANN201, D100, D103, F403
# type: ignore
from peewee import *


def up(migrator, db):
    migrator.migrate(
        migrator.drop_not_null("torrent", "announce"),
    )


def down(migrator, db):
    migrator.migrate(
        migrator.add_not_null("torrent", "announce"),
    )
