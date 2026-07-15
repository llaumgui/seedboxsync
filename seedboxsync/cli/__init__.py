# -*- coding: utf-8 -*-
#
# Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
import click
import logging
import seedboxsync
from flask.cli import with_appcontext
from seedboxsync import create_app
from .cli import Cli, command, group, pass_context
from seedboxsync.cli.context import Context
from seedboxsync.core import Database

__all__ = [
    "Cli",
    "Context",
    "command",
    "group",
    "pass_context",
]

CONTEXT_SETTINGS = {
    "help_option_names": ["-h", "--help"],
}
VERSION_BANNER = """Script for performing sync operations between your NAS and your seedbox.

SeedboxSync %s
SeedboxSync database %s""" % (
    seedboxsync.__version__,
    Database.DATABASE_VERSION,
)


@click.group(
    "seedboxsync",
    help="Script for sync operations between your NAS and your seedbox",
    cls=Cli,
    context_settings=CONTEXT_SETTINGS,
    create_app=create_app,
    no_args_is_help=True,
    add_default_commands=False,
    add_version_option=False,
    load_dotenv=False,
)
@click.version_option(version=seedboxsync.__version__, prog_name="SeedboxSync", message=VERSION_BANNER)
@pass_context
@with_appcontext
def cli(ctx: Context) -> None:
    """
    SeedboxSync CLI entrypoint.

    Args:
        ctx (Context): The Click context object.
    """
    if ctx.app.debug:
        ctx.app.logger.setLevel(logging.DEBUG)
