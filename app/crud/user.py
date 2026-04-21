from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserCreate
from app.security import hash_password


def get_user_by_username(db: Session, username: str) -> User | None:
    return db.query(User).filter(User.username == username).first()


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()


def create_user(db: Session, user_in: UserCreate) -> User:
    user = User(
        username=user_in.username,
        email=user_in.email,
        password_hash=hash_password(user_in.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def build_unique_username(db: Session, email: str) -> str:
    base = email.split("@", 1)[0].strip().lower() or "user"
    candidate = base
    suffix = 1

    while get_user_by_username(db, candidate):
        candidate = f"{base}{suffix}"
        suffix += 1

    return candidate
