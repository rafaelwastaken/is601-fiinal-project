import pytest
from pydantic import ValidationError

from app.schemas.user import UserCreate


def test_user_create_rejects_invalid_email():
    with pytest.raises(ValidationError):
        UserCreate(username="rafael", email="not-an-email", password="password123")


def test_user_create_rejects_short_password():
    with pytest.raises(ValidationError):
        UserCreate(username="rafael", email="rafael@example.com", password="short")
