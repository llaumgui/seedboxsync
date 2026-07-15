# -*- coding: utf-8 -*-
#
# Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
"""
All commands related to synchronization operations in SeedboxSync.
"""

import glob
import os
from paramiko import SSHException
from seedboxsync.core.dao import Torrent
from seedboxsync.core.utils import get_torrent_infos
from seedboxsync.core import fs, current_app as app

LOCK_NAME="sync-blackhole"

def blackhole(dry_run: bool, ping: bool) -> None:
    """
    Perform the blackhole synchronization.

    Uploads torrent files from the local watch folder to the seedbox.
    Handles creation of lock files, optional dry-run, file permissions,
    database persistence, and error handling.

    Args:
        ctx (Context): The Click context object.
        dry_run (bool): Whether to perform a dry run.
        ping (bool): Whether to ping a service during execution.
    """
    if not app.seedboxsync_config.get("sync_blackhole_enabled") or False:
        app.logger.info("Blackhole synchronization task is disabled")
        return

    app.logger.debug('blackhole dry-run: "%s"' % dry_run)

    # Call ping_start_hook if enabled
    if ping:
        app.ping.start("sync_blackhole")

    # Gather all torrent files
    local_watch_path = app.seedboxsync_config.get("local_watch_path") or ""
    app.logger.debug('Scanning for torrent files in "%s"' % local_watch_path)
    torrents = glob.glob(fs.join(fs.abspath(local_watch_path), "*.torrent"))
    if len(torrents) > 0:
        for torrent_file in torrents:
            torrent_name = os.path.basename(torrent_file)
            if not dry_run:
                tmp_path = app.seedboxsync_config.get("seedbox_tmp_path") or ""
                watch_path = app.seedboxsync_config.get("seedbox_watch_path") or ""

                app.logger.info('Upload torrent: "%s"' % torrent_name)
                app.logger.debug('Upload "%s" to "%s"' % (torrent_file, tmp_path))

                try:
                    app.sync.put(torrent_file, os.path.join(tmp_path, torrent_name))

                    # Apply chmod if configured
                    chmod = app.seedboxsync_config.get("seedbox_chmod") or False
                    if isinstance(chmod, str):
                        app.logger.debug("Change permissions to %s" % chmod)
                        app.sync.chmod(os.path.join(tmp_path, torrent_name), int(chmod, 8))

                    # Move file from tmp to watch directory
                    app.logger.debug('Move from "%s" to "%s"' % (tmp_path, watch_path))
                    app.sync.rename(
                        os.path.join(tmp_path, torrent_name),
                        os.path.join(watch_path, torrent_name),
                    )

                    # Store torrent info in database
                    torrent_info = get_torrent_infos(torrent_file) or None
                    torrent = Torrent.create(name=torrent_name)
                    if torrent_info is not None and isinstance(torrent_info, dict):
                        torrent.announce = torrent_info.get("announce") or None
                        torrent.save()

                        # Remove local torrent file
                        app.logger.debug('Remove local torrent "%s"' % torrent_file)
                        os.remove(torrent_file)
                    else:
                        app.logger.warning('Rename local "%s" to .torrent.fail' % torrent_file)
                        os.rename(torrent_file, torrent_file + ".fail")
                except SSHException as exc:
                    app.logger.warning("SSH client exception > %s" % str(exc))
            else:
                app.logger.info('Dry-run: not uploading torrent "%s"' % torrent_name)
    else:
        app.logger.info('No torrent files found in "%s"' % app.seedboxsync_config.get("local_watch_path"))

    # Call ping_success_hook if enabled
    if ping:
        app.ping.success("sync_blackhole")
