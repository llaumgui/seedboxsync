# -*- coding: utf-8 -*-
#
# Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
"""
SeedboxSync sync service for seedbox.
"""

import datetime
import os
import re
from paramiko import SSHException
from seedboxsync.core import fs, current_app as app
from seedboxsync.core.dao import Download
from seedboxsync.core.taskmanager import track_taskstatus
from seedboxsync.core.sync.download_progress import DownloadProgress
from seedboxsync.core.exception import SeedboxSyncConfigurationError

LOCK_NAME = "sync-seedbox"


@track_taskstatus(LOCK_NAME)
def seedbox(dry_run: bool, ping: bool, only_store: bool) -> None:
    """
    Perform synchronization from the seedbox.

    Downloads files from the remote seedbox to the local machine,
    supports optional dry-run and only-store modes, applies exclusion patterns,
    and persists download information in the database.

    Args:
        dry_run (bool): Whether to list files without downloading or persisting them.
        ping (bool): Whether to ping the configured monitoring service.
        only_store (bool): Whether to record remote files without downloading them.
    """
    if not app.seedboxsync_config.get("sync_seedbox_enabled") or False:
        app.logger.info("Seedbox synchronization task is disabled")
        return

    app.logger.debug('sync_seedbox dry-run: "%s"' % dry_run)
    app.logger.debug('sync_seedbox only-store: "%s"' % only_store)

    # Call ping_start_hook if enabled
    if ping:
        app.ping.start("sync_seedbox")

    finished_path = app.seedboxsync_config.get("seedbox_finished_path") or ""
    part_suffix = app.seedboxsync_config.get("seedbox_part_suffix")
    app.logger.debug('Scanning files in "%s"' % finished_path)

    # Walk through all files on the seedbox
    try:
        try:
            app.sync.chdir(finished_path)
        except FileNotFoundError as exc:
            app.logger.error(f"{str(exc)}\nFailed to scan directory: {finished_path}")
            return

        for walker in app.sync.walk(""):  # type: ignore[attr-defined]
            for filename in walker[2]:
                filepath = os.path.join(walker[0], filename)
                if os.path.splitext(filename)[1] == part_suffix:
                    app.logger.debug('Skipping part file "%s"' % filename)
                elif Download.is_already_download(filepath):
                    app.logger.debug('Skipping already downloaded file "%s"' % filename)
                elif __exclude_by_pattern(filepath):
                    app.logger.debug('Skipping excluded file "%s"' % filename)
                else:
                    if not dry_run:
                        __get_file(filepath, only_store)
                    else:
                        app.logger.info('Dry-run: not downloading "%s"' % filepath)
    except (IOError, FileNotFoundError) as exc:
        app.logger.error('SeedboxSyncError > "%s"' % exc)

    # Call ping_success_hook if enabled
    if ping:
        app.ping.success("sync_seedbox")


def __exclude_by_pattern(filepath: str) -> bool:
    """
    Determine if a file should be excluded from synchronization based on patterns.

    Args:
        ctx (Context): The Click context object.
        filepath (str): Path of the file to check.

    Returns:
        bool: True if the file matches the exclude pattern, False otherwise.

    Raises:
        SeedboxSyncConfigurationError: If the exclude pattern is invalid.
    """
    pattern = app.seedboxsync_config.get("seedbox_exclude_syncing") or ""
    if not pattern:
        return False

    try:
        return re.search(pattern, filepath) is not None
    except re.error:
        raise SeedboxSyncConfigurationError("Invalid configuration for exclude_syncing! See https://docs.python.org/3/library/re.html")


def __get_file(filepath: str, only_store: bool) -> None:
    """
    Download a single file from the seedbox.

    Handles file path creation, partial download suffix, database persistence,
    size verification, and renaming after successful download.

    Args:
        ctx (Context): The Click context object.
        filepath (str): Path of the file on the seedbox.
        only_store (bool): Whether to record the file without downloading it.
    """
    local_filepath = fs.join(app.seedboxsync_config.get("local_download_path") or "", filepath)
    part_suffix = app.seedboxsync_config.get("seedbox_part_suffix") or ""
    local_filepath_part = local_filepath + part_suffix
    local_path = os.path.dirname(fs.abspath(local_filepath))

    # Create local directory tree if necessary
    if not only_store:
        fs.ensure_dir_exists(local_path)
    app.logger.debug('Download: "%s" to "%s"' % (filepath, local_path))

    try:
        seedbox_size = app.sync.stat(filepath).st_size  # type: ignore[attr-defined]
        if seedbox_size == 0:
            app.logger.warning('Empty file: "%s" (%s)' % (filepath, str(seedbox_size)))

        download = Download.create(path=filepath, seedbox_size=seedbox_size)
        download.save()

        if not only_store:
            app.logger.info('Downloading "%s"' % filepath)
            progress_callback = DownloadProgress(download)
            app.sync.get(filepath, local_filepath_part, progress_callback=progress_callback)
            local_size = os.stat(local_filepath_part).st_size

            if local_size == 0 or local_size != seedbox_size:
                app.logger.error('Download failed: "%s" (%s/%s)' % (filepath, str(local_size), str(seedbox_size)))

            os.rename(local_filepath_part, local_filepath)
        else:
            app.logger.info('Marking as downloaded "%s"' % filepath)
            local_size = seedbox_size

        download.local_size = local_size
        download.finished = datetime.datetime.now()
        download.save()
    except SSHException as exc:
        app.logger.error("Download failed: %s" % str(exc))
