"""Recommend data access layer."""
from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.recommend import UserBehavior, Recommendation, ABTestConfig


class BehaviorRepo:
    BEHAVIOR_SCORES = {"view": 1.0, "click": 2.0, "cart": 3.0, "purchase": 5.0, "rate": 4.0}

    @staticmethod
    def record(session: Session, user_id: int, product_id: int, behavior_type: str) -> UserBehavior:
        score = BehaviorRepo.BEHAVIOR_SCORES.get(behavior_type, 1.0)
        behavior = UserBehavior(user_id=user_id, product_id=product_id,
                                behavior_type=behavior_type, score=score)
        session.add(behavior)
        session.flush()
        return behavior

    @staticmethod
    def get_user_behaviors(session: Session, user_id: int, limit: int = 100) -> list[UserBehavior]:
        return session.query(UserBehavior).filter(
            UserBehavior.user_id == user_id
        ).order_by(UserBehavior.created_at.desc()).limit(limit).all()


class RecommendRepo:
    @staticmethod
    def save_recommendations(session: Session, items: list[dict], user_id: int,
                             strategy: str, ab_group: str = "A") -> None:
        for item in items:
            rec = Recommendation(
                user_id=user_id, product_id=item["product_id"],
                score=item["score"], strategy=strategy, ab_group=ab_group,
            )
            session.add(rec)
        session.flush()

    @staticmethod
    def get_history(session: Session, user_id: int, strategy: str | None = None,
                    limit: int = 20) -> list[Recommendation]:
        query = session.query(Recommendation).filter(Recommendation.user_id == user_id)
        if strategy:
            query = query.filter(Recommendation.strategy == strategy)
        return query.order_by(Recommendation.created_at.desc()).limit(limit).all()


class ABTestRepo:
    @staticmethod
    def get_active(session: Session) -> ABTestConfig | None:
        return session.query(ABTestConfig).filter(ABTestConfig.is_active == 1).first()

    @staticmethod
    def create(session: Session, name: str, strategy_a: str, strategy_b: str,
               ratio: float = 0.5) -> ABTestConfig:
        config = ABTestConfig(name=name, strategy_a=strategy_a,
                              strategy_b=strategy_b, ratio=ratio)
        session.add(config)
        session.flush()
        return config
