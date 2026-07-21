from pathlib import Path
import pytest
from seedboxsync.core import fs


def test_ensure_dir_exists_creates_missing_directory(tmp_path):
    directory = tmp_path / "nested"

    fs.ensure_dir_exists(str(directory))

    assert directory.is_dir()


def test_ensure_dir_exists_rejects_existing_file(tmp_path):
    filepath = tmp_path / "file"
    filepath.write_text("content")

    with pytest.raises(AssertionError, match="is not a directory"):
        fs.ensure_dir_exists(str(filepath))


def test_join_expands_first_path_and_appends_components(tmp_path):
    assert fs.join(str(tmp_path), "shows", "episode.mkv") == str(Path(tmp_path, "shows", "episode.mkv"))
