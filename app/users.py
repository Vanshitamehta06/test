"""In-memory user accounts with salted PBKDF2 password hashing."""
from __future__ import annotations

import hashlib
import hmac
import re
import secrets
from dataclasses import dataclass

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
MIN_PASSWORD_LENGTH = 8
_ITERATIONS = 200_000


class AccountExistsError(Exception):
    pass


class InvalidAccountError(ValueError):
    pass


@dataclass
class User:
    email: str
    salt: bytes
    password_hash: bytes


def _hash(password: str, salt: bytes) -> bytes:
    return hashlib.pbkdf2_hmac("sha256", password.encode(), salt, _ITERATIONS)


class UserStore:
    def __init__(self) -> None:
        self._users: dict[str, User] = {}
        self._sessions: dict[str, str] = {}

    @staticmethod
    def normalize(email: str) -> str:
        return email.strip().lower()

    def register(self, email: str, password: str) -> User:
        email = self.normalize(email)
        if not EMAIL_RE.match(email):
            raise InvalidAccountError("Enter a valid email address.")
        if len(password) < MIN_PASSWORD_LENGTH:
            raise InvalidAccountError(f"Password must be at least {MIN_PASSWORD_LENGTH} characters.")
        if email in self._users:
            raise AccountExistsError("An account with this email already exists.")
        salt = secrets.token_bytes(16)
        user = User(email=email, salt=salt, password_hash=_hash(password, salt))
        self._users[email] = user
        return user

    def authenticate(self, email: str, password: str) -> str | None:
        """Return a new session token, or None if the credentials are wrong."""
        user = self._users.get(self.normalize(email))
        if user is None:
            # Hash anyway so response time does not reveal whether the email exists.
            _hash(password, secrets.token_bytes(16))
            return None
        if not hmac.compare_digest(_hash(password, user.salt), user.password_hash):
            return None
        token = secrets.token_urlsafe(32)
        self._sessions[token] = user.email
        return token

    def user_for_token(self, token: str) -> str | None:
        return self._sessions.get(token)
