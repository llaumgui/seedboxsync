import io
import sys
import pytest
from tests.main import SeedboxSyncTest, hash_output
import seedboxsync


def test_seedboxsync_base(tmp):
    """
    Test base commands.
    """

    help_output = "c266d92ea36b7d31088d969274639d52"
    _, tmp_config_files, tmp_db_file, tmp_watch = tmp

    # seedboxsync
    with SeedboxSyncTest(config_files=tmp_config_files) as app:
        captured_output = io.StringIO()
        sys.stdout = captured_output
        try:
            app.run()
        finally:
            sys.stdout = sys.__stdout__
        output = captured_output.getvalue()
        assert hash_output(output) == help_output
        # Test tmp mock
        assert app.config['local']['db_file'] == tmp_db_file
        assert app.config['local']['watch_path'] == tmp_watch

    # seedboxsync -h (SystemExit 0)
    argv = ['-h']
    captured_output = io.StringIO()
    sys.stdout = captured_output
    try:
        with pytest.raises(SystemExit) as excinfo:
            with SeedboxSyncTest(argv=argv, config_files=tmp_config_files) as app:
                app.run()
        assert excinfo.value.code == 0
    finally:
        sys.stdout = sys.__stdout__
    output = captured_output.getvalue()
    assert hash_output(output) == help_output

    # seedboxsync -v (SystemExit 0)
    argv = ['-v']
    captured_output = io.StringIO()
    sys.stdout = captured_output
    try:
        with pytest.raises(SystemExit) as excinfo:
            with SeedboxSyncTest(argv=argv, config_files=tmp_config_files) as app:
                app.run()
        assert excinfo.value.code == 0
    finally:
        sys.stdout = sys.__stdout__
    output = captured_output.getvalue()
    assert ('SeedboxSync ' + seedboxsync.__version__) in output

    # seedboxsync --version (SystemExit 0)
    argv = ['--version']
    captured_output = io.StringIO()
    sys.stdout = captured_output
    try:
        with pytest.raises(SystemExit) as excinfo:
            with SeedboxSyncTest(argv=argv, config_files=tmp_config_files) as app:
                app.run()
        assert excinfo.value.code == 0
    finally:
        sys.stdout = sys.__stdout__
    output = captured_output.getvalue()
    assert ('SeedboxSync ' + seedboxsync.__version__) in output
