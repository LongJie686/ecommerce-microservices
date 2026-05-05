"""User business logic - registration uses transaction to ensure atomicity."""
from __future__ import annotations

from sqlalchemy.orm import Session

from app.repositories.user_repo import UserRepo
from app.schemas.user import ProfileUpdateRequest
from shared.auth import create_token
from shared.response import success, error, paginated


def _hash_password(password: str) -> str:
    import bcrypt
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def _verify_password(password: str, password_hash: str) -> bool:
    import bcrypt
    return bcrypt.checkpw(password.encode(), password_hash.encode())


class UserService:
    def register(self, session: Session, username: str, password: str, nickname: str = ""):
        if UserRepo.get_by_username(session, username):
            return error("Username already exists", code=409)

        user = UserRepo.create_user(
            session,
            username=username,
            password_hash=_hash_password(password),
            nickname=nickname,
        )
        session.flush()
        return success({"id": user.id, "username": user.username})

    def login(self, session: Session, username: str, password: str, jwt_secret: str, jwt_expire_hours: int = 24):
        user = UserRepo.get_by_username(session, username)
        if not user or not _verify_password(password, user.password_hash):
            return error("Invalid username or password", code=401)
        if user.status != 1:
            return error("Account is disabled", code=403)

        token = create_token(
            {"user_id": user.id, "username": user.username},
            secret=jwt_secret, expire_hours=jwt_expire_hours,
        )
        return success({
            "token": token,
            "user": {"id": user.id, "username": user.username, "nickname": user.nickname},
        })

    def get_profile(self, session: Session, user_id: int):
        user = UserRepo.get_by_id(session, user_id)
        if not user:
            return error("User not found", code=404)

        profile = UserRepo.get_profile(session, user_id)
        return success({
            "user": {"id": user.id, "username": user.username, "nickname": user.nickname, "avatar": user.avatar},
            "profile": {
                "age": profile.age if profile else None,
                "gender": profile.gender if profile else None,
                "preferred_categories": profile.preferred_categories if profile else "",
                "tags": profile.tags if profile else "",
            },
        })

    def update_profile(self, session: Session, user_id: int, data: ProfileUpdateRequest):
        user = UserRepo.get_by_id(session, user_id)
        if not user:
            return error("User not found", code=404)

        profile = UserRepo.update_profile(
            session, user_id,
            age=data.age, gender=data.gender,
            preferred_categories=data.preferred_categories,
            price_range=data.price_range,
            tags=data.tags,
        )
        return success({"user_id": profile.user_id, "tags": profile.tags})

    def list_users(self, session: Session, page: int = 1, page_size: int = 20):
        users, total = UserRepo.list_users(session, page, page_size)
        items = [{"id": u.id, "username": u.username, "nickname": u.nickname} for u in users]
        return paginated(items, total, page, page_size)
