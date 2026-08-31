import importlib
import sys
from unittest.mock import MagicMock, patch


def test_app_module_exports_application_created_at_import():
    expected_app = MagicMock(name="application")

    with patch("seedboxsync.create_app", return_value=expected_app) as create_app:
        sys.modules.pop("seedboxsync.app", None)
        app_module = importlib.import_module("seedboxsync.app")

    create_app.assert_called_once_with()
    assert app_module.app is expected_app
