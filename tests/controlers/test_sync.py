import pytest
import os
from tests.main import SeedboxSyncTest, hash_output
from seedboxsync.core.dao.torrent import Torrent
from peewee import fn


def test_seedboxsync_sync(tmp):
    """
    Test sync command.
    """

    _, tmp_config_files, _, _ = tmp

    # seedboxsync sync -h (SystemExit 0)
    argv = ['sync', '-h']
    with pytest.raises(SystemExit) as excinfo:
        with SeedboxSyncTest(argv=argv, config_files=tmp_config_files) as app:
            app.run()
    assert excinfo.value.code == 0


def test_seedboxsync_sync_blackhole(tmp, capsys, mock_sftp):
    """
    Test sync blackhole command with empty watch dir.
    """

    _, tmp_config_files, _, tmp_watch_path = tmp

    # seedboxsync sync blackhole -h (SystemExit 0)
    argv = ['sync', 'blackhole', '-h']
    with pytest.raises(SystemExit) as excinfo:
        with SeedboxSyncTest(argv=argv, config_files=tmp_config_files) as app:
            app.run()
    assert excinfo.value.code == 0

    # seedboxsync sync blackhole
    argv = ['sync', 'blackhole']
    with SeedboxSyncTest(argv=argv, config_files=tmp_config_files) as app:
        app.run()
        output = capsys.readouterr().err
        assert app.exit_code == 0  # No error code
        assert hash_output(output) == 'f93396c51a8ae2b40b2390aee0c1cb42'  # Message is good
        assert not os.path.isfile(os.path.join(tmp_watch_path, 'Fedora-Server-dvd-x86_64-32.torrent'))  # Torrent file is removed
        uploaded = Torrent.select(fn.COUNT(Torrent.id).alias('count')).where(Torrent.name.contains('Fedora-Server-dvd-x86_64-32'))
        count = uploaded.scalar()
        assert count == 1  # One torrent uploaded

    # seedboxsync sync blackhole (with empty watch folder)
    argv = ['sync', 'blackhole']
    with SeedboxSyncTest(argv=argv, config_files=tmp_config_files) as app:
        app.run()
        output = capsys.readouterr().err
        assert app.exit_code == 0
        assert 'No torrent files found in ' in output

    """
    Test sync seedbox command.
    """

    _, tmp_config_files, _, _ = tmp

    # seedboxsync sync seedbox -h (SystemExit 0)
    argv = ['sync', 'seedbox', '-h']
    with pytest.raises(SystemExit) as excinfo:
        with SeedboxSyncTest(argv=argv, config_files=tmp_config_files) as app:
            app.run()
    assert excinfo.value.code == 0

    # seedboxsync sync seedbox
    argv = ['sync', 'seedbox']
    with SeedboxSyncTest(argv=argv, config_files=tmp_config_files) as app:
        app.run()
        output = capsys.readouterr().err
        print(output)
        assert app.exit_code == 0  # No error code
        assert output == ''
