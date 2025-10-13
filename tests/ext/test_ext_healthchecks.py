from seedboxsync.ext.ext_healthchecks import healthchecks_ping_start_hook, healthchecks_ping_success_hook
from tests.main import SeedboxSyncTest

ping_url = 'https://healthchecks.dev/ping/12345678-1234-1234-1234-123456789012'


def test_healthchecks_ping(tmp, mock_urllib):
    """
    Test seedboxsync without any subcommands or arguments.
    """

    _, tmp_config_files, _, _ = tmp

    with SeedboxSyncTest(config_files=tmp_config_files) as app:
        # Set config
        app.config.set('healthchecks', 'sync_seedbox', {
            'enabled': 'true',
            'ping_url': ping_url
        })

        # Defined start
        healthchecks_ping_start_hook(app, 'sync_seedbox')
        mock_urllib.assert_called_once()
        called_url, = mock_urllib.call_args[0]
        assert called_url == ping_url + '/start'

        # Defined stuccess
        healthchecks_ping_success_hook(app, 'sync_seedbox')
        assert mock_urllib.call_count == 2
        called_url, = mock_urllib.call_args[0]
        assert called_url == ping_url

        # Undefined start and stuccess
        healthchecks_ping_start_hook(app, 'sync_blackhole')
        healthchecks_ping_success_hook(app, 'sync_blackhole')
        assert mock_urllib.call_count == 2

        app.run()  # Run to close safty
