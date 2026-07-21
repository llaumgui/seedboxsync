import logging
from unittest.mock import MagicMock
import click
from seedboxsync.core.logger import ColorFormatter, configure_logger


def test_color_formatter_colors_known_levels_and_preserves_unknown_levels(monkeypatch):
    formatter = ColorFormatter("%(levelname)s %(message)s")
    warning = logging.LogRecord("test", logging.WARNING, __file__, 1, "careful", (), None)
    custom = logging.LogRecord("test", 15, __file__, 1, "plain", (), None)
    styled = MagicMock(return_value="colored warning")
    monkeypatch.setattr(click, "style", styled)

    assert formatter.format(warning) == "colored warning"
    styled.assert_called_once_with("WARNING careful", fg="yellow")
    assert formatter.format(custom) == "Level 15 plain"


def test_configure_logger_applies_formatter_to_every_handler():
    logger = logging.getLogger("seedboxsync-test-configure")
    handlers = [MagicMock(), MagicMock()]
    logger.handlers = handlers

    configure_logger(logger)

    for handler in handlers:
        formatter = handler.setFormatter.call_args.args[0]
        assert isinstance(formatter, ColorFormatter)
