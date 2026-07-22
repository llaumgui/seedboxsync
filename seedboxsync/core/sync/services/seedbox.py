#
# Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
"""SeedboxSync sync service for seedbox."""

import datetime
from os import PathLike, fspath
from pathlib import Path
import re
from paramiko import SSHException
from seedboxsync.core import current_app as app, utils
from seedboxsync.core.dao import Download
from seedboxsync.core.exception import SeedboxSyncConfigurationError
from seedboxsync.core.sync.download_progress import DownloadProgress
from seedboxsync.core.taskmanager import track_taskstatus

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
    if not app.seedboxsync_config.get("sync_seedbox_enabled"):
        app.logger.info("Seedbox synchronization task is disabled")
        return

    app.logger.debug(f'sync seedbox dry-run: "{dry_run}"')
    app.logger.debug(f'sync seeddbox only-store: "{only_store}"')
    app.logger.debug(f'sync seedbox ping: "{ping}"')

    # Call ping.start() if enabled
    if ping:
        app.ping.start("sync_seedbox")

    finished_path = app.seedboxsync_config.get("seedbox_finished_path", "")
    part_suffix = app.seedboxsync_config.get("seedbox_part_suffix")
    app.logger.debug(f'Scanning files in "{finished_path}"')

    # Walk through all files on the seedbox
    try:
        try:
            app.sync.chdir(None)  # type: ignore[arg-type]
            app.sync.chdir(finished_path)
        except FileNotFoundError as exc:
            app.logger.error(f"{exc!s}\nFailed to scan directory: {finished_path}")
            return

        for root, _, filenames in app.sync.walk(""):  # type: ignore[attr-defined]
            root = Path(root)

            for filename in filenames:
                filepath = root / filename

                if filepath.suffix == part_suffix:
                    app.logger.debug(f'Skipping part file "{filename}"')
                elif Download.is_already_download(filepath):
                    app.logger.debug(f'Skipping already downloaded file "{filename}"')
                elif __exclude_by_pattern(filepath):
                    app.logger.debug(f'Skipping excluded file "{filename}"')
                else:
                    if dry_run:
                        app.logger.info(f'Dry-run: not downloading "{filepath}"')
                        continue

                    __get_file(filepath, only_store)

    except (OSError, FileNotFoundError) as exc:
        app.logger.error(f'SeedboxSyncError > "{exc}"')

    # Call ping.success() if enabled
    if ping:
        app.ping.success("sync_seedbox")


def __exclude_by_pattern(filepath: str | PathLike[str]) -> bool:
    """
    Determine if a file should be excluded from synchronization based on patterns.

    Args:
        ctx (Context): The Click context object.
        filepath (str | PathLike[str]): Path of the file to check.

    Returns:
        bool: True if the file matches the exclude pattern, False otherwise.

    Raises:
        SeedboxSyncConfigurationError: If the exclude pattern is invalid.
    """
    pattern = app.seedboxsync_config.get("seedbox_exclude_syncing", "")
    filepath = fspath(filepath)
    if not pattern:
        return False

    try:
        return re.search(pattern, filepath) is not None
    except re.error as exc:
        raise SeedboxSyncConfigurationError("Invalid configuration for exclude_syncing! See https://docs.python.org/3/library/re.html") from exc


def __get_file(filepath: str | PathLike[str], only_store: bool) -> None:
    """
    Download a single file from the seedbox.

    Handles file path creation, partial download suffix, database persistence,
    size verification, and renaming after successful download.

    Args:
        ctx (Context): The Click context object.
        filepath (str): Path of the file on the seedbox.
        only_store (bool): Whether to record the file without downloading it.
    """
    filepath = fspath(filepath)
    local_filepath = Path(app.seedboxsync_config.get("local_download_path", "")).expanduser().resolve() / filepath
    part_suffix = app.seedboxsync_config.get("seedbox_part_suffix", "")
    local_filepath_part = local_filepath.with_suffix(part_suffix)
    local_path = local_filepath.expanduser().resolve().parent

    # Create local directory tree if necessary
    if not only_store:
        utils.ensure_dir_exists(local_path)
    app.logger.debug(f'Download: "{filepath}" to "{local_path}"')

    try:
        seedbox_size = app.sync.stat(filepath).st_size  # type: ignore[attr-defined]
        if seedbox_size == 0:
            app.logger.warning(f'Empty file: "{filepath}" ({seedbox_size!s})')

        download = Download.create(path=filepath, seedbox_size=seedbox_size)
        download.save()

        if not only_store:
            app.logger.info(f'Downloading "{filepath}"')
            progress_callback = DownloadProgress(download)
            app.sync.get(filepath, local_filepath_part, progress_callback=progress_callback)
            local_size = Path(local_filepath_part).stat().st_size

            if local_size == 0 or local_size != seedbox_size:
                app.logger.error(f'Download failed: "{filepath}" ({local_size!s}/{seedbox_size!s})')

            Path(local_filepath_part).rename(local_filepath)
        else:
            app.logger.info(f'Marking as downloaded "{filepath}"')
            local_size = seedbox_size

        download.local_size = local_size
        download.finished = datetime.datetime.now()
        download.save()
    except SSHException as exc:
        app.logger.error(f"Download failed: {exc!s}")
