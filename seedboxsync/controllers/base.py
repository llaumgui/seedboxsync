# -*- coding: utf-8 -*-
#
# Copyright (C) 2015-2025 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
import seedboxsync
from cement import Controller  # type: ignore[attr-defined]
from cement.utils.version import get_version_banner
from seedboxsync.core.db import Database

VERSION_BANNER = """
Script for performing sync operations between your NAS and your seedbox.

SeedboxSync %s
SeedboxSync database %s
%s
""" % (seedboxsync.__version__, Database.DATABASE_VERSION, get_version_banner())


class Base(Controller):
    """
    Base controller for SeedboxSync CLI application.

    Provides common configuration for the CLI, including:
    - Description displayed in help messages.
    - Epilog usage examples.
    - Global arguments such as version banner.
    """

    class Meta:
        label = 'base'

        # Short description displayed at the top of --help output
        description = 'Script for sync operations between your NAS and your seedbox'

        # Text displayed at the bottom of --help output
        epilog = 'Usage: seedboxsync sync blackhole --dry-run'

        # Controller-level arguments (e.g., 'seedboxsync --version')
        arguments = [
            # Add a version banner with -v / --version
            (['-v', '--version'],
             {'action': 'version',
              'version': VERSION_BANNER}),
        ]

    def _default(self) -> None:
        """
        Default action when no sub-command is provided.

        Prints the help message for the CLI.
        """
        self.app.args.print_help()  # type: ignore[attr-defined]
