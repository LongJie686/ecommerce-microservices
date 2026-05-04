"""Recommend business logic - strategy selection, AB testing, caching."""
from __future__ import annotations

import hashlib

from sqlalchemy.orm import Session

from app.algorithms import CollaborativeFiltering, ContentBasedRecommender, HotRecommender, HybridRecommender
from app.repositories.recommend_repo import BehaviorRepo, RecommendRepo, ABTestRepo
from app.schemas.recommend import BehaviorRequest, RecommendRequest
from shared.cache import RedisClient
from shared.response import success, error


STRATEGIES = {
    "cf": CollaborativeFiltering(),
    "content": ContentBasedRecommender(),
    "hot": HotRecommender(),
    "hybrid": HybridRecommender(),
}


class RecommendService:
    def __init__(self, redis: RedisClient, cache_ttl: int = 180):
        self._redis = redis
        self._cache_ttl = cache_ttl

    def record_behavior(self, session: Session, req: BehaviorRequest):
        behavior = BehaviorRepo.record(session, req.user_id, req.product_id, req.behavior_type)
        return success({"id": behavior.id, "behavior_type": behavior.behavior_type})

    async def get_recommendations(self, session: Session, req: RecommendRequest):
        cache_key = f"rec:{req.user_id}:{req.strategy}:{req.top_k}"
        cached = await self._redis.get_with_anti_penetration(cache_key)
        if cached is not None:
            return success(cached)

        # AB test check
        ab_config = ABTestRepo.get_active(session)
        strategy = req.strategy
        ab_group = "A"

        if ab_config:
            bucket = int(hashlib.md5(str(req.user_id).encode()).hexdigest(), 16) % 100
            if bucket < ab_config.ratio * 100:
                strategy = ab_config.strategy_a
                ab_group = "A"
            else:
                strategy = ab_config.strategy_b
                ab_group = "B"

        engine = STRATEGIES.get(strategy, STRATEGIES["hybrid"])

        if strategy == "hot":
            results = engine.recommend(session, top_k=req.top_k)
        elif strategy in ("cf", "content"):
            results = engine.recommend(session, req.user_id, top_k=req.top_k)
        else:
            results = engine.recommend(session, req.user_id, top_k=req.top_k)

        RecommendRepo.save_recommendations(session, results, req.user_id, strategy, ab_group)

        await self._redis.cache_with_anti_penetration(cache_key, results, expire=self._cache_ttl)
        return success({"items": results, "strategy": strategy, "ab_group": ab_group})

    def get_history(self, session: Session, user_id: int, strategy: str | None = None):
        recs = RecommendRepo.get_history(session, user_id, strategy)
        items = [{"product_id": r.product_id, "score": r.score,
                  "strategy": r.strategy, "ab_group": r.ab_group} for r in recs]
        return success(items)
