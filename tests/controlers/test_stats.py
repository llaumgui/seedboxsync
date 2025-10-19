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
        assert hash_output(output) == '9ed7172a6aee56a1d28d4865251a4ce9'


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
        assert hash_output(output) == 'e3e6455164feee1f9ca6a71cb0def6e8'


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
        assert hash_output(output) == '15ada03fe3fa4f2e2a924d3b4324d535'
