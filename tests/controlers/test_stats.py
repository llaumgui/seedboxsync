from tests.main import SeedboxSyncTest, hash_output


def test_seedboxsync_stats_by_month(tmp):
    """
    Test stats by month command.
    """

    _, tmp_config_files, _, _ = tmp

    # seedboxsync stats by-month
    argv = ['stats', 'by-month']
    with SeedboxSyncTest(argv=argv, config_files=tmp_config_files) as app:
        app.run()
        data, output = app.last_rendered
        assert hash_output(output) == '5bdf7b91831435e54b7d07fa0f2655f0'


def test_seedboxsync_stats_by_year(tmp):
    """
    Test stats by year command.
    """

    _, tmp_config_files, _, _ = tmp

    # seedboxsync stats by-year
    argv = ['stats', 'by-year']
    with SeedboxSyncTest(argv=argv, config_files=tmp_config_files) as app:
        app.run()
        data, output = app.last_rendered
        assert hash_output(output) == '442aad79ee2a0b24ca777f548a7186d5'


def test_seedboxsync_stats_total(tmp):
    """
    Test total stats command.
    """

    _, tmp_config_files, _, _ = tmp

    # seedboxsync stats by-year
    argv = ['stats', 'total']
    with SeedboxSyncTest(argv=argv, config_files=tmp_config_files) as app:
        app.run()
        data, output = app.last_rendered
        assert hash_output(output) == '4720f936a04601467e42c54ecafb603a'
