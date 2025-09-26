import io
import sys
import pytest
from tests.main import SeedboxSyncTest
import seedboxsync


def test_seedboxsync_base():
    """
    Test base commands.
    """

    help_output = "c266d92ea36b7d31088d969274639d52"

    # seedboxsync
    with SeedboxSyncTest(config_dirs=SeedboxSyncTest.get_config_dirs()) as app:
        captured_output = io.StringIO()
        sys.stdout = captured_output
        try:
            app.run()
        finally:
            sys.stdout = sys.__stdout__
        output = captured_output.getvalue()
        assert SeedboxSyncTest.hash_output(output) == help_output

    # seedboxsync -h (SystemExit 0)
    argv = ['-h']
    captured_output = io.StringIO()
    sys.stdout = captured_output
    try:
        with pytest.raises(SystemExit) as excinfo:
            with SeedboxSyncTest(argv=argv, config_dirs=SeedboxSyncTest.get_config_dirs()) as app:
                app.run()
        assert excinfo.value.code == 0
    finally:
        sys.stdout = sys.__stdout__
    output = captured_output.getvalue()
    assert SeedboxSyncTest.hash_output(output) == help_output

    # seedboxsync -v (SystemExit 0)
    argv = ['-v']
    captured_output = io.StringIO()
    sys.stdout = captured_output
    try:
        with pytest.raises(SystemExit) as excinfo:
            with SeedboxSyncTest(argv=argv, config_dirs=SeedboxSyncTest.get_config_dirs()) as app:
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
            with SeedboxSyncTest(argv=argv, config_dirs=SeedboxSyncTest.get_config_dirs()) as app:
                app.run()
        assert excinfo.value.code == 0
    finally:
        sys.stdout = sys.__stdout__
    output = captured_output.getvalue()
    assert ('SeedboxSync ' + seedboxsync.__version__) in output
