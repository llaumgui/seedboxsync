# -*- coding: utf-8 -*-
#
# Copyright (C) 2015-2025 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#

import signal
from cement import App, TestApp
from cement.core.exc import CaughtSignal
from .core.db import extend_db, close_db
from .core.exc import SeedboxSyncError
from .core.sync.sync import extend_sync, close_sync
from .core.init_defaults import CONFIG
from .controllers.base import Base
from .controllers.clean import Clean
from .controllers.search import Search
from .controllers.sync import Sync


class SeedboxSync(App):
    """SeedboxSync application."""

    class Meta:
        label = 'seedboxsync'

        # configuration defaults
        config_defaults = CONFIG

        # call sys.exit() on close
        exit_on_close = True

        # load additional framework extensions
        extensions = [
            'yaml',
            'colorlog',
            'tabulate',
            'print',
            'seedboxsync.ext.ext_bcoding',
            'seedboxsync.ext.ext_lock',
            'seedboxsync.ext.ext_healthchecks'
        ]

        # configuration handler
        config_handler = 'yaml'

        # configuration file suffix
        config_file_suffix = '.yml'

        # set the log handler
        framework_logging = False
        log_handler = 'colorlog'

        # set the output handler
        output_handler = 'tabulate'

        # register handlers
        handlers = [
            Base,
            Clean,
            Search,
            Sync
        ]

        # register hook
        hooks = [
            ('pre_run', extend_sync),
            ('pre_close', close_sync),
            ('post_setup', extend_db),
            ('post_run', close_db)
        ]

        # define customs hooks
        define_hooks = [
            'ping_start_hook',
            'ping_success_hook'
        ]

        # catch signal
        catch_signals = [
            signal.SIGTERM,
            signal.SIGINT,
            signal.SIGHUP,
        ]


class SeedboxSyncTest(TestApp, SeedboxSync):
    """A sub-class of SeedboxSync that is better suited for testing."""

    class Meta:
        label = 'seedboxsync'


def main():
    with SeedboxSync() as app:
        try:
            app.run()

        except AssertionError as e:
            print('AssertionError > %s' % e.args[0])
            app.exit_code = 1

            if app.debug is True:
                import traceback
                traceback.print_exc()

        except SeedboxSyncError as e:
            print('SeedboxSyncError > %s' % e.args[0])
            app.exit_code = 1

            if app.debug is True:
                import traceback
                traceback.print_exc()

        except (CaughtSignal, KeyboardInterrupt) as e:
            # Default Cement signals are SIGINT and SIGTERM, exit 0 (non-error)
            app.exit_code = 0
            if e.signum == signal.SIGTERM:
                app.log.warning('Caught SIGTERM')
            elif e.signum == signal.SIGINT:
                app.log.warning('Caught SIGINT')
            else:
                app.log.warning('Stopped')
            app.close()


if __name__ == '__main__':
    main()
