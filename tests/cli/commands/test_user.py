from unittest.mock import patch
from werkzeug.security import check_password_hash
from seedboxsync.cli import cli
from seedboxsync.core.database.models import User


def test_user_list_filters_and_limits_results(app, runner):
    with app.app_context():
        User.create(username="alice", email="alice@example.com", password="hash")
        User.create(username="bob", email="bob@example.com", password="hash")

    result = runner.invoke(cli, ["user", "list", "--search", "ali", "--number", "1"])

    assert result.exit_code == 0
    assert "alice@example.com" in result.output
    assert "bob@example.com" not in result.output


def test_user_delete_reports_missing_user(runner):
    result = runner.invoke(cli, ["user", "delete", "--id", "999999"])

    assert result.exit_code == 0
    assert "does not exist" in result.output


def test_user_delete_can_be_cancelled(app, runner):
    with app.app_context():
        user = User.create(username="alice", email="alice@example.com", password="hash")
        user_id = user.id

    result = runner.invoke(cli, ["user", "delete", "--id", str(user_id)], input="n\n")

    assert result.exit_code == 0
    assert "Operation canceled." in result.output
    with app.app_context():
        assert User.get_or_none(User.id == user_id) is not None


def test_user_delete_removes_confirmed_user(app, runner):
    with app.app_context():
        user = User.create(username="alice", email="alice@example.com", password="hash")
        user_id = user.id

    result = runner.invoke(cli, ["user", "delete", "--id", str(user_id), "--yes"])

    assert result.exit_code == 0
    assert "deleted successfully" in result.output
    with app.app_context():
        assert User.get_or_none(User.id == user_id) is None


def test_user_add_rejects_duplicate_username_or_email(app, runner):
    with app.app_context():
        User.create(username="alice", email="alice@example.com", password="hash")

    result = runner.invoke(cli, ["user", "add", "-u", "alice", "-e", "new@example.com", "-p", "secret"])

    assert result.exit_code == 0
    assert "already exists" in result.output


def test_user_add_creates_hashed_user(app, runner):
    result = runner.invoke(cli, ["user", "add", "-u", "alice", "-e", "alice@example.com", "-p", "secret"])

    assert result.exit_code == 0
    assert "created successfully" in result.output
    with app.app_context():
        user = User.get(User.username == "alice")
        assert check_password_hash(user.password, "secret")


def test_user_edit_reports_missing_user(runner):
    result = runner.invoke(cli, ["user", "edit", "--id", "999999", "-u", "alice"])

    assert result.exit_code == 0
    assert "does not exist" in result.output


def test_user_edit_rejects_duplicate_username(app, runner):
    with app.app_context():
        User.create(username="alice", email="alice@example.com", password="hash")
        bob = User.create(username="bob", email="bob@example.com", password="hash")

    result = runner.invoke(cli, ["user", "edit", "--id", str(bob.id), "-u", "alice"])

    assert result.exit_code == 0
    assert "already taken" in result.output


def test_user_edit_updates_fields_and_password(app, runner):
    with app.app_context():
        user = User.create(username="alice", email="alice@example.com", password="old")
        user_id = user.id

    with patch("seedboxsync.cli.commands.cmd_user.generate_password_hash", return_value="new-hash") as hash_password:
        result = runner.invoke(cli, ["user", "edit", "--id", str(user_id), "-u", "updated", "-e", "updated@example.com", "-p", "new"])

    assert result.exit_code == 0
    assert "updated successfully" in result.output
    hash_password.assert_called_once_with("new")
    with app.app_context():
        user = User.get_by_id(user_id)
        assert user.username == "updated"
        assert user.email == "updated@example.com"
        assert user.password == "new-hash"
