# -*- coding: utf-8 -*-
#
# Copyright (C) 2015-2025 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
from cement import App  # type: ignore[attr-defined]
import socket
import urllib.request


def healthchecks_ping_start_hook(app: App, sub_command: str) -> None:
    """
    Send a start ping to Healthchecks for a given subcommand.

    Args:
        app (App): The Cement App object.
        sub_command (str): The SeedboxSync subcommand to ping.
    """
    sub_command_config = app.config.get('healthchecks', sub_command)
    if sub_command_config['enabled'] is False:
        app.log.warning("Healthchecks for \"%s\" disabled by configuration" % sub_command)
    else:
        ping_url = sub_command_config['ping_url'] + '/start'
        app.log.debug('Ping url: %s' % ping_url)

        try:
            urllib.request.urlopen(ping_url, timeout=10)
        except socket.error as e:
            app.log.error("Healthchecks, ping failed: %s" % e)
            pass


def healthchecks_ping_success_hook(app: App, sub_command: str) -> None:
    """
    Send a success ping to Healthchecks for a given subcommand.

    Args:
        app (App): The Cement App object.
        sub_command (str): The SeedboxSync subcommand to ping.
    """
    sub_command_config = app.config.get('healthchecks', sub_command)
    if sub_command_config['enabled'] is False:
        app.log.warning("Healthchecks for \"%s\" disabled by configuration" % sub_command)
    else:
        ping_url = sub_command_config['ping_url']
        app.log.debug('Ping url: %s' % ping_url)

        try:
            urllib.request.urlopen(ping_url, timeout=10)
        except socket.error as e:
            app.log.error("Healthchecks, ping failed: %s" % e)
            pass


def healthchecks_post_setup_hook(app: App) -> None:
    """
    Post-setup hook to extend SeedboxSync with Healthchecks support.

    Registers ping hooks if the 'healthchecks' section exists in the configuration.

    Args:
        app (App): The Cement App object.
    """
    if app.config.has_section('healthchecks'):
        app.log.debug('Extending seedboxsync application with Healthchecks')
        app.hook.register('ping_start_hook', healthchecks_ping_start_hook)
        app.hook.register('ping_success_hook', healthchecks_ping_success_hook)
    else:
        app.log.debug('Not extending seedboxsync application with Healthchecks')


def load(app: App) -> None:
    """
    Registers the Healthchecks post-setup hook.

    Args:
        app (App): The Cement App object.
    """
    app.hook.register('post_setup', healthchecks_post_setup_hook)
