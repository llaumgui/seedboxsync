# -*- coding: utf-8 -*-
#
# Copyright (C) 2015-2025 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#

from cement import Controller
from cement.utils.version import get_version_banner
import seedboxsync

VERSION_BANNER = """
Script for sync operations between your NAS and your seedbox

SeedboxSync %s
%s
""" % (seedboxsync.__version__, get_version_banner())


class Base(Controller):
    class Meta:
        label = 'base'

        # text displayed at the top of --help output
        description = 'Script for sync operations between your NAS and your seedbox'

        # text displayed at the bottom of --help output
        epilog = 'Usage: seedboxsync sync blackhole --dry-run'

        # controller level arguments. ex: 'seedboxsync --version'
        arguments = [
            # add a version banner
            (['-v', '--version'],
             {'action': 'version',
              'version': VERSION_BANNER}),
        ]

    def _default(self):
        """Default action if no sub-command is passed."""

        self.app.args.print_help()
