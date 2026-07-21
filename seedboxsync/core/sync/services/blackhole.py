#
# Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
"""SeedboxSync sync service for blackhole."""

import glob
import os
from pathlib import Path
from paramiko import SSHException
from seedboxsync.core import current_app as app, fs
from seedboxsync.core.dao import Torrent
from seedboxsync.core.taskmanager import track_taskstatus
from seedboxsync.core.utils import get_torrent_infos

LOCK_NAME = "sync-blackhole"


@track_taskstatus(LOCK_NAME)
def blackhole(dry_run: bool, ping: bool) -> None:
    """
    Perform the blackhole synchronization.

    Uploads torrent files from the local watch folder to the seedbox.
    Optional dry-run, file permissions, database persistence, and error handling.

    Args:
        dry_run (bool): Whether to perform a dry run.
        ping (bool): Whether to ping a service during execution.
    """
    if not app.seedboxsync_config.get("sync_blackhole_enabled"):
        app.logger.info("Blackhole synchronization task is disabled")
        return

    app.logger.debug(f'sync blackhole dry-run: "{dry_run}"')
    app.logger.debug(f'sync blackhole ping: "{ping}"')

    # Call ping.start() if enabled
    if ping:
        app.ping.start("sync_blackhole")

    # Gather all torrent files
    local_watch_path = app.seedboxsync_config.get("local_watch_path", "")
    app.logger.debug(f'Scanning for torrent files in "{local_watch_path}"')
    torrents = glob.glob(fs.join(fs.abspath(local_watch_path), "*.torrent"))

    if len(torrents) == 0:
        app.logger.info('No torrent files found in "{}"'.format(app.seedboxsync_config.get("local_watch_path")))
        # Call ping.success() if enabled
        if ping:
            app.ping.success("sync_blackhole")
        return

    for torrent_file in torrents:
        torrent_name = os.path.basename(torrent_file)

        # Dry-run mode
        if dry_run:
            app.logger.info(f'Dry-run: not uploading torrent "{torrent_name}"')
            continue

        tmp_path = app.seedboxsync_config.get("seedbox_tmp_path", "")
        watch_path = app.seedboxsync_config.get("seedbox_watch_path", "")

        app.logger.info(f'Upload torrent: "{torrent_name}"')
        app.logger.debug(f'Upload "{torrent_file}" to "{tmp_path}"')

        try:
            app.sync.chdir(None)   # type: ignore[arg-type]
            app.sync.put(torrent_file, os.path.join(tmp_path, torrent_name))

            # Apply chmod if configured
            chmod = app.seedboxsync_config.get("seedbox_chmod", False)
            if isinstance(chmod, str):
                app.logger.debug(f"Change permissions to {chmod}")
                app.sync.chmod(os.path.join(tmp_path, torrent_name), int(chmod, 8))

            # Move file from tmp to watch directory
            app.logger.debug(f'Move from "{tmp_path}" to "{watch_path}"')
            app.sync.rename(
                os.path.join(tmp_path, torrent_name),
                os.path.join(watch_path, torrent_name),
            )

            # Store torrent info in database
            torrent_info = get_torrent_infos(torrent_file)
            torrent = Torrent.create(name=torrent_name)
            if torrent_info is not None and isinstance(torrent_info, dict):
                torrent.announce = torrent_info.get("announce")
                torrent.save()

                # Remove local torrent file
                app.logger.debug(f'Remove local torrent "{torrent_file}"')
                Path(torrent_file).unlink()
            else:
                app.logger.warning(f'Rename local "{torrent_file}" to .torrent.fail')
                Path(torrent_file).rename(torrent_file + ".fail")
        except SSHException as exc:
            app.logger.warning(f"SSH client exception > {exc!s}")

    # Call ping.success() if enabled
    if ping:
        app.ping.success("sync_blackhole")
