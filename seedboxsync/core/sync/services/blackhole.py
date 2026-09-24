#
# Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
"""SeedboxSync sync service for blackhole."""

from os import fspath
from pathlib import Path
from paramiko import SSHException
from seedboxsync.core import current_app
from seedboxsync.core.database.models import Torrent
from seedboxsync.core.taskmanager import track_taskstatus

LOCK_NAME = "sync-blackhole"
PRIORITY = 10


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
    if not current_app.seedboxsync_config.get("sync_blackhole_enabled"):
        current_app.logger.info("Blackhole synchronization task is disabled")
        return

    current_app.logger.debug(f'sync blackhole dry-run: "{dry_run}"')
    current_app.logger.debug(f'sync blackhole ping: "{ping}"')

    # Call ping.start() if enabled
    if ping:
        current_app.ping.start("sync_blackhole")

    # Gather all torrent files
    local_watch_path = current_app.seedboxsync_config.get("local_watch_path", "")
    current_app.logger.debug(f'Scanning for torrent files in "{local_watch_path}"')
    torrents = list(Path(local_watch_path).expanduser().resolve().glob("*.torrent"))

    if len(torrents) == 0:
        current_app.logger.info('No torrent files found in "{}"'.format(current_app.seedboxsync_config.get("local_watch_path")))
        # Call ping.success() if enabled
        if ping:
            current_app.ping.success("sync_blackhole")
        return

    for torrent_file in torrents:
        torrent_name = torrent_file.name

        # Dry-run mode
        if dry_run:
            current_app.logger.info(f'Dry-run: not uploading torrent "{torrent_name}"')
            continue

        tmp_path = current_app.seedboxsync_config.get("seedbox_tmp_path", "")
        watch_path = current_app.seedboxsync_config.get("seedbox_watch_path", "")

        current_app.logger.info(f'Upload torrent: "{torrent_name}"')
        current_app.logger.debug(f'Upload "{torrent_file}" to "{tmp_path}"')

        try:
            current_app.sync.chdir(None)  # type: ignore[arg-type]
            current_app.sync.put(torrent_file, Path(tmp_path) / torrent_name)

            # Apply chmod if configured
            chmod = current_app.seedboxsync_config.get("seedbox_chmod", False)
            if isinstance(chmod, str):
                current_app.logger.debug(f"Change permissions to {chmod}")
                current_app.sync.chmod(Path(tmp_path) / torrent_name, int(chmod, 8))

            # Move file from tmp to watch directory
            current_app.logger.debug(f'Move from "{tmp_path}" to "{watch_path}"')
            current_app.sync.rename(
                Path(tmp_path) / torrent_name,
                Path(watch_path) / torrent_name,
            )

            # Store torrent info in database
            torrent = Torrent.create(name=torrent_name)
            if torrent.set_from_file(torrent_file):
                torrent.save()

                # Remove local torrent file
                current_app.logger.debug(f'Remove local torrent "{torrent_file}"')
                Path(torrent_file).unlink()
            else:
                current_app.logger.warning(f'Rename local "{torrent_file}" to .torrent.fail')
                Path(torrent_file).rename(fspath(torrent_file) + ".fail")
        except SSHException as exc:
            current_app.logger.warning(f"SSH client exception > {exc!s}")

    # Call ping.success() if enabled
    if ping:
        current_app.ping.success("sync_blackhole")
