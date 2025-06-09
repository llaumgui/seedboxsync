from tests.main import SeedboxSyncTest


def test_seedboxsync_stats_by_month():
    """
    Test stats by month command.
    """

    # seedboxsync stats by-month
    argv = ['stats', 'by-month']
    with SeedboxSyncTest(argv=argv, config_dirs=SeedboxSyncTest.get_config_dirs()) as app:
        app.run()
        data, output = app.last_rendered
        assert SeedboxSyncTest.hash_output(output) == '5bdf7b91831435e54b7d07fa0f2655f0'


def test_seedboxsync_stats_by_year():
    """
    Test stats by year command.
    """

    # seedboxsync stats by-year
    argv = ['stats', 'by-year']
    with SeedboxSyncTest(argv=argv, config_dirs=SeedboxSyncTest.get_config_dirs()) as app:
        app.run()
        data, output = app.last_rendered
        assert SeedboxSyncTest.hash_output(output) == '442aad79ee2a0b24ca777f548a7186d5'


def test_seedboxsync_stats_total():
    """
    Test total stats command.
    """

    # seedboxsync stats by-year
    argv = ['stats', 'total']
    with SeedboxSyncTest(argv=argv, config_dirs=SeedboxSyncTest.get_config_dirs()) as app:
        app.run()
        data, output = app.last_rendered
        assert SeedboxSyncTest.hash_output(output) == '4720f936a04601467e42c54ecafb603a'
