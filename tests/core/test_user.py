from werkzeug.security import generate_password_hash
from seedboxsync.core.dao import User


def test_authenticate_accepts_username_or_email(app):
    with app.app_context():
        user = User.create(
            username="alice",
            password=generate_password_hash("secret"),
            email="alice@example.com",
        )

        assert User.authenticate("alice", "secret").id == user.id
        assert User.authenticate("alice@example.com", "secret").id == user.id


def test_authenticate_returns_none_for_unknown_user_or_wrong_password(app):
    with app.app_context():
        User.create(
            username="alice",
            password=generate_password_hash("secret"),
            email="alice@example.com",
        )

        assert User.authenticate("unknown", "secret") is None
        assert User.authenticate("alice", "wrong") is None
