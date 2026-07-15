def test_seedboxsync_config_reflects_runtime_updates(app):
    """Configuration changes must remain visible after the first lookup."""
    initial_config = app.seedboxsync_config

    app.config["SEEDBOXSYNC_SYNC_SEEDBOX_ENABLED"] = True

    assert initial_config["sync_seedbox_enabled"] is False
    assert app.seedboxsync_config["sync_seedbox_enabled"] is True
