"""Recommendation algorithms - collaborative filtering, content-based, hybrid."""
from __future__ import annotations

import random
from collections import defaultdict
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.models.recommend import UserBehavior


def _build_user_item_matrix(behaviors: list[UserBehavior]) -> dict[int, dict[int, float]]:
    matrix: dict[int, dict[int, float]] = defaultdict(lambda: defaultdict(float))
    for b in behaviors:
        matrix[b.user_id][b.product_id] += b.score
    return dict(matrix)


def _cosine_similarity(vec_a: dict[int, float], vec_b: dict[int, float]) -> float:
    common = set(vec_a.keys()) & set(vec_b.keys())
    if not common:
        return 0.0
    dot = sum(vec_a[k] * vec_b[k] for k in common)
    norm_a = sum(v ** 2 for v in vec_a.values()) ** 0.5
    norm_b = sum(v ** 2 for v in vec_b.values()) ** 0.5
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


class CollaborativeFiltering:
    """User-based collaborative filtering."""

    def recommend(self, session: Session, user_id: int, top_k: int = 10) -> list[dict[str, Any]]:
        all_behaviors = session.query(UserBehavior).limit(10000).all()
        matrix = _build_user_item_matrix(all_behaviors)

        if user_id not in matrix:
            return []

        target_vec = matrix[user_id]
        similarities: list[tuple[int, float]] = []
        for uid, vec in matrix.items():
            if uid != user_id:
                sim = _cosine_similarity(target_vec, vec)
                if sim > 0:
                    similarities.append((uid, sim))

        similarities.sort(key=lambda x: x[1], reverse=True)
        top_neighbors = similarities[:20]

        candidate_scores: dict[int, float] = defaultdict(float)
        for neighbor_id, sim in top_neighbors:
            for pid, score in matrix[neighbor_id].items():
                if pid not in target_vec:
                    candidate_scores[pid] += sim * score

        ranked = sorted(candidate_scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
        return [{"product_id": pid, "score": round(score, 4), "strategy": "cf"} for pid, score in ranked]


class ContentBasedRecommender:
    """Content-based using user profile preferences."""

    def recommend(self, session: Session, user_id: int, top_k: int = 10,
                  preferred_categories: list[int] | None = None) -> list[dict[str, Any]]:
        behaviors = session.query(UserBehavior).filter(
            UserBehavior.user_id == user_id
        ).order_by(UserBehavior.created_at.desc()).limit(100).all()

        interacted = {b.product_id for b in behaviors}

        query = session.execute(
            text("SELECT id, sales_count FROM products WHERE status = 1 LIMIT 500")
        )
        candidates = []
        for row in query:
            pid, sales = row[0], row[1]
            if pid not in interacted:
                score = 1.0 + (sales or 0) * 0.01
                if preferred_categories:
                    score *= 1.5
                candidates.append({"product_id": pid, "score": round(score, 4), "strategy": "content"})

        candidates.sort(key=lambda x: x["score"], reverse=True)
        return candidates[:top_k]


class HotRecommender:
    """Popularity-based recommendation (fallback for cold-start)."""

    def recommend(self, session: Session, top_k: int = 10) -> list[dict[str, Any]]:
        query = session.execute(
            text("SELECT id, sales_count FROM products WHERE status = 1 "
                 "ORDER BY sales_count DESC LIMIT :limit"),
            {"limit": top_k},
        )
        return [{"product_id": row[0], "score": float(row[1] or 0), "strategy": "hot"} for row in query]


class HybridRecommender:
    """Hybrid: weighted combination of CF + content + hot."""

    def __init__(self):
        self.cf = CollaborativeFiltering()
        self.content = ContentBasedRecommender()
        self.hot = HotRecommender()

    def recommend(self, session: Session, user_id: int, top_k: int = 10,
                  preferred_categories: list[int] | None = None) -> list[dict[str, Any]]:
        cf_results = self.cf.recommend(session, user_id, top_k=top_k * 2)
        content_results = self.content.recommend(session, user_id, top_k=top_k * 2,
                                                  preferred_categories=preferred_categories)
        hot_results = self.hot.recommend(session, top_k=top_k)

        merged: dict[int, float] = defaultdict(float)
        for item in cf_results:
            merged[item["product_id"]] += item["score"] * 0.5
        for item in content_results:
            merged[item["product_id"]] += item["score"] * 0.3
        for item in hot_results:
            merged[item["product_id"]] += item["score"] * 0.2

        ranked = sorted(merged.items(), key=lambda x: x[1], reverse=True)[:top_k]
        return [{"product_id": pid, "score": round(score, 4), "strategy": "hybrid"} for pid, score in ranked]
