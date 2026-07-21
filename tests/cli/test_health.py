from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch
from urllib.error import URLError
import pytest
from seedboxsync.cli import cli
from seedboxsync.core.dao import TaskStatus


def _set_heartbeat(app, *, age: timedelta = timedelta()) -> None:
    with app.app_context():
        TaskStatus.replace(
            key="heartbeat",
            running=False,
            started=datetime.now() - age,
            finished=datetime.now() - age,
        ).execute()


def _web_response(status: int) -> MagicMock:
    response = MagicMock(status=status)
    response.__enter__.return_value = response
    return response


def test_health_reports_all_healthy_components(app, runner):
    _set_heartbeat(app)

    with patch("seedboxsync.cli.commands.cmd_health.urlopen", return_value=_web_response(200)) as urlopen:
        result = runner.invoke(cli, ["health"])

    assert result.exit_code == 0
    assert "CLI - OK" in result.output
    assert "Task manager - OK" in result.output
    assert "WebUI - OK" in result.output
    urlopen.assert_called_once_with("http://127.0.0.1:5000/healthcheck", timeout=5)


@pytest.mark.parametrize(
    ("heartbeat_age", "expected_exit"),
    [
        (None, 2),
        (timedelta(minutes=6), 3),
    ],
)
def test_health_reports_missing_or_stale_task_manager(app, runner, heartbeat_age, expected_exit):
    if heartbeat_age is not None:
        _set_heartbeat(app, age=heartbeat_age)

    with patch("seedboxsync.cli.commands.cmd_health.urlopen", return_value=_web_response(200)):
        result = runner.invoke(cli, ["health"])

    assert result.exit_code == expected_exit
    assert "Task manager - NOK" in result.output


@pytest.mark.parametrize(
    ("urlopen_result", "expected_exit"),
    [
        (_web_response(503), 5),
        (URLError("connection refused"), 6),
    ],
)
def test_health_reports_webui_failures(app, runner, urlopen_result, expected_exit):
    _set_heartbeat(app)
    side_effect = urlopen_result if isinstance(urlopen_result, Exception) else None
    return_value = None if side_effect else urlopen_result

    with patch("seedboxsync.cli.commands.cmd_health.urlopen", return_value=return_value, side_effect=side_effect):
        result = runner.invoke(cli, ["health"])

    assert result.exit_code == expected_exit
    assert "WebUI - NOK" in result.output
