import pytest
from seedboxsync.core import utils


def test_ensure_dir_exists_creates_missing_directory(tmp_path):
    directory = tmp_path / "nested"

    utils.ensure_dir_exists(str(directory))

    assert directory.is_dir()


def test_ensure_dir_exists_rejects_existing_file(tmp_path):
    filepath = tmp_path / "file"
    filepath.write_text("content")

    with pytest.raises(AssertionError, match="is not a directory"):
        utils.ensure_dir_exists(str(filepath))
