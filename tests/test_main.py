from seedboxsync.main import SeedboxSyncTest


def test_seedboxsync():
    """
    Test seedboxsync without any subcommands or arguments.
    """

    with SeedboxSyncTest() as app:
        app.run()
        assert app.exit_code == 0


def test_seedboxsync_debug():
    """
    Test that debug mode is functional.
    """

    with SeedboxSyncTest() as app:
        app.run()
        assert app.debug is False

    argv = ['--debug']
    with SeedboxSyncTest(argv=argv) as app:
        app.run()
        assert app.debug is True
