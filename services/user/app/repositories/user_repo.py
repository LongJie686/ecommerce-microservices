"""User data access layer - encapsulates all SQL operations."""
from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.user import User, UserRole, UserProfile


class UserRepo:
    @staticmethod
    def get_by_username(session: Session, username: str) -> User | None:
        return session.query(User).filter(User.username == username).first()

    @staticmethod
    def get_by_id(session: Session, user_id: int) -> User | None:
        return session.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_profile(session: Session, user_id: int) -> UserProfile | None:
        return session.query(UserProfile).filter(UserProfile.user_id == user_id).first()

    @staticmethod
    def create_user(session: Session, username: str, password_hash: str, nickname: str = "") -> User:
        user = User(username=username, password_hash=password_hash, nickname=nickname or username)
        session.add(user)
        session.flush()

        session.add(UserRole(user_id=user.id, role="user"))
        session.add(UserProfile(user_id=user.id))
        session.flush()

        return user

    @staticmethod
    def update_profile(session: Session, user_id: int, **kwargs) -> UserProfile:
        profile = session.query(UserProfile).filter(UserProfile.user_id == user_id).first()
        if not profile:
            profile = UserProfile(user_id=user_id)
            session.add(profile)
            session.flush()

        for key, value in kwargs.items():
            if value is not None and hasattr(profile, key):
                setattr(profile, key, value)

        session.flush()
        return profile

    @staticmethod
    def list_users(session: Session, page: int = 1, page_size: int = 20) -> tuple[list[User], int]:
        query = session.query(User).filter(User.status == 1)
        total = query.count()
        users = query.offset((page - 1) * page_size).limit(page_size).all()
        return users, total
