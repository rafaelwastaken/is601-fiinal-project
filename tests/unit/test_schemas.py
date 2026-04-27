import pytest
from pydantic import ValidationError

from app.schemas.user import PasswordChangeRequest, UserCreate


def test_user_create_rejects_invalid_email():
    with pytest.raises(ValidationError):
        UserCreate(username="rafael", email="not-an-email", password="password123")


def test_user_create_rejects_short_password():
    with pytest.raises(ValidationError):
        UserCreate(username="rafael", email="rafael@example.com", password="short")


def test_password_change_request_rejects_short_new_password():
    with pytest.raises(ValidationError):
        PasswordChangeRequest(current_password="password123", new_password="short")
