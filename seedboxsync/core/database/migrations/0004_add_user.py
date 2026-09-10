# Generated from a schema diff on 2026-09-12 10:24.
# ruff: noqa: ANN001, ANN201, D100, D103, F403, F405
# type: ignore
import datetime
from peewee import *


def up(migrator, db):
    class User(Model):
        username = CharField(unique=True)
        password = CharField()
        origin = CharField(max_length=10, default="local")
        email = CharField(unique=True)
        created = DateTimeField(default=datetime.datetime.now)
        last_login = DateTimeField(null=True)

        class Meta:
            database = db
            table_name = "user"

    db.create_tables([User])
    User.create(
        username="admin",
        password="scrypt:32768:8:1$2xZqYGaVsWgvXn8Q$b0ef299478983c1ce62090ae4a7830a09fedff434835cb983ad96a2"
        "e3719d180bf2256fe0109cf89a6d01f5ffe0159450d527ad331bb5e29e9392565c6782417",  # sonar:python:S2068=false
        email="admin@admin.ltd",
    )


def down(migrator, db):
    migrator.migrate(migrator.drop_table("user"))
