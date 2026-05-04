"""Analytics business logic - dashboard stats, price distribution, sales trends."""
from __future__ import annotations

from sqlalchemy.orm import Session
from sqlalchemy import text

from shared.response import success, error


class AnalyticsService:
    def dashboard(self, session: Session):
        product_stats = session.execute(text(
            "SELECT COUNT(*) as total, AVG(price) as avg_price, "
            "MIN(price) as min_price, MAX(price) as max_price "
            "FROM products WHERE status = 1"
        )).fetchone()

        category_dist = session.execute(text(
            "SELECT c.name, COUNT(p.id) as cnt "
            "FROM categories c LEFT JOIN products p ON c.id = p.category_id AND p.status = 1 "
            "GROUP BY c.id, c.name ORDER BY cnt DESC LIMIT 10"
        )).fetchall()

        top_sales = session.execute(text(
            "SELECT name, sales_count, price FROM products WHERE status = 1 "
            "ORDER BY sales_count DESC LIMIT 10"
        )).fetchall()

        return success({
            "product_overview": {
                "total": product_stats[0] if product_stats else 0,
                "avg_price": round(float(product_stats[1] or 0), 2),
                "min_price": float(product_stats[2] or 0),
                "max_price": float(product_stats[3] or 0),
            },
            "category_distribution": [
                {"name": row[0], "count": row[1]} for row in category_dist
            ],
            "top_sales": [
                {"name": row[0], "sales": row[1], "price": float(row[2] or 0)} for row in top_sales
            ],
        })

    def price_distribution(self, session: Session, category: str | None = None):
        query = "SELECT price FROM products WHERE status = 1"
        params = {}
        if category:
            query += " AND category_id IN (SELECT id FROM categories WHERE name = :cat)"
            params["cat"] = category

        rows = session.execute(text(query), params).fetchall()
        prices = [float(r[0]) for r in rows if r[0]]

        if not prices:
            return success({"ranges": [], "total": 0})

        ranges = [
            {"label": "0-100", "min": 0, "max": 100},
            {"label": "100-500", "min": 100, "max": 500},
            {"label": "500-1000", "min": 500, "max": 1000},
            {"label": "1000-3000", "min": 1000, "max": 3000},
            {"label": "3000+", "min": 3000, "max": float("inf")},
        ]

        distribution = []
        for r in ranges:
            count = sum(1 for p in prices if r["min"] <= p < r["max"])
            distribution.append({"range": r["label"], "count": count, "percentage": round(count / len(prices) * 100, 1)})

        return success({"distribution": distribution, "total": len(prices), "avg": round(sum(prices) / len(prices), 2)})

    def sales_trend(self, session: Session, category: str | None = None, days: int = 7):
        query = """
            SELECT DATE(created_at) as d, COUNT(*) as products, SUM(sales_count) as sales
            FROM products WHERE status = 1 AND created_at >= DATE_SUB(NOW(), INTERVAL :days DAY)
        """
        params = {"days": days}
        if category:
            query += " AND category_id IN (SELECT id FROM categories WHERE name = :cat)"
            params["cat"] = category

        query += " GROUP BY DATE(created_at) ORDER BY d"
        rows = session.execute(text(query), params).fetchall()

        return success({
            "trend": [{"date": str(row[0]), "products": row[1], "sales": row[2] or 0} for row in rows],
        })

    def shop_comparison(self, session: Session, platform: str | None = None):
        query = """
            SELECT shop_name, COUNT(*) as cnt, AVG(rating) as avg_rating,
                   SUM(sales_count) as total_sales
            FROM products WHERE status = 1
        """
        params = {}
        if platform:
            query += " AND source = :platform"
            params["platform"] = platform

        query += " GROUP BY shop_name ORDER BY total_sales DESC LIMIT 20"
        rows = session.execute(text(query), params).fetchall()

        return success({
            "shops": [
                {"name": row[0], "product_count": row[1],
                 "avg_rating": round(float(row[2] or 0), 1), "total_sales": row[3] or 0}
                for row in rows
            ],
        })
