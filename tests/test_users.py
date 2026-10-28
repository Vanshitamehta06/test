import pytest

from app.users import AccountExistsError, InvalidAccountError, UserStore


def test_register_and_authenticate():
    store = UserStore()
    store.register("Ana@Example.com", "correct-horse")
    token = store.authenticate("ana@example.com", "correct-horse")
    assert token
    assert store.user_for_token(token) == "ana@example.com"


def test_wrong_password_and_unknown_email_rejected():
    store = UserStore()
    store.register("ana@example.com", "correct-horse")
    assert store.authenticate("ana@example.com", "wrong-password") is None
    assert store.authenticate("nobody@example.com", "correct-horse") is None


def test_password_is_not_stored_in_plain_text():
    store = UserStore()
    user = store.register("ana@example.com", "correct-horse")
    assert b"correct-horse" not in user.password_hash


def test_duplicate_and_invalid_registrations_rejected():
    store = UserStore()
    store.register("ana@example.com", "correct-horse")
    with pytest.raises(AccountExistsError):
        store.register("ANA@example.com", "another-password")
    with pytest.raises(InvalidAccountError):
        store.register("not-an-email", "correct-horse")
    with pytest.raises(InvalidAccountError):
        store.register("bo@example.com", "short")
