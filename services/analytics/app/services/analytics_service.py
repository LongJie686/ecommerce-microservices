"""Analytics business logic - dashboard stats, price distribution, sales trends."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.analytics import PriceStats, SalesTrend, ShopRanking
from shared.response import success


class AnalyticsService:
    def dashboard(self, session: Session):
        price_row = session.query(
            func.sum(PriceStats.product_count).label("total"),
            func.avg(PriceStats.price_avg).label("avg_price"),
            func.min(PriceStats.price_min).label("min_price"),
            func.max(PriceStats.price_max).label("max_price"),
        ).first()

        category_dist = (
            session.query(PriceStats.category, PriceStats.product_count)
            .order_by(PriceStats.product_count.desc())
            .limit(10)
            .all()
        )

        top_shops = (
            session.query(ShopRanking.shop_name, ShopRanking.total_sales, ShopRanking.avg_rating)
            .order_by(ShopRanking.total_sales.desc())
            .limit(10)
            .all()
        )

        return success({
            "product_overview": {
                "total": int(price_row.total or 0),
                "avg_price": round(float(price_row.avg_price or 0), 2),
                "min_price": round(float(price_row.min_price or 0), 2),
                "max_price": round(float(price_row.max_price or 0), 2),
            },
            "category_distribution": [
                {"name": row.category, "count": row.product_count} for row in category_dist
            ],
            "top_sales": [
                {"name": row.shop_name, "sales": row.total_sales,
                 "avg_rating": round(float(row.avg_rating or 0), 1)}
                for row in top_shops
            ],
        })

    def price_distribution(self, session: Session, category: str | None = None):
        query = session.query(PriceStats)
        if category:
            query = query.filter(PriceStats.category == category)
        rows = query.all()

        if not rows:
            return success({"distribution": [], "total": 0})

        total = sum(r.product_count for r in rows)
        return success({
            "distribution": [
                {
                    "category": r.category,
                    "price_min": r.price_min,
                    "price_max": r.price_max,
                    "price_avg": round(r.price_avg, 2),
                    "price_median": round(r.price_median, 2),
                    "count": r.product_count,
                    "percentage": round(r.product_count / total * 100, 1) if total else 0,
                }
                for r in rows
            ],
            "total": total,
        })

    def sales_trend(self, session: Session, category: str | None = None, days: int = 7):
        cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%d")
        query = session.query(SalesTrend).filter(SalesTrend.date >= cutoff)
        if category:
            query = query.filter(SalesTrend.category == category)
        rows = query.order_by(SalesTrend.date).all()

        return success({
            "trend": [
                {
                    "date": row.date,
                    "products": row.product_count,
                    "sales": row.total_sales,
                    "revenue": row.total_revenue,
                }
                for row in rows
            ],
        })

    def shop_comparison(self, session: Session, platform: str | None = None):
        query = session.query(ShopRanking)
        if platform:
            query = query.filter(ShopRanking.platform == platform)
        rows = query.order_by(ShopRanking.total_sales.desc()).limit(20).all()

        return success({
            "shops": [
                {
                    "name": row.shop_name,
                    "platform": row.platform,
                    "product_count": row.product_count,
                    "avg_rating": round(float(row.avg_rating or 0), 1),
                    "total_sales": row.total_sales,
                }
                for row in rows
            ],
        })
