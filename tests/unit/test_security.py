from app.security import hash_password, verify_password


def test_hash_password_is_not_plain_text():
    password = "supersecret123"
    hashed = hash_password(password)
    assert hashed != password


def test_verify_password_matches_hash():
    password = "supersecret123"
    hashed = hash_password(password)
    assert verify_password(password, hashed) is True
    assert verify_password("wrongpass", hashed) is False
