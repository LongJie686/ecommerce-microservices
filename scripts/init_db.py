"""Initialize databases and create tables for all services."""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.database import Base, DatabaseManager


def init_all_databases():
    services = {
        "user": {
            "url": os.getenv("DATABASE_URL", "mysql+pymysql://root:root123@localhost:3306/ecommerce_user"),
        },
        "product": {
            "url": os.getenv("DATABASE_URL", "mysql+pymysql://root:root123@localhost:3306/ecommerce_product"),
        },
        "recommend": {
            "url": os.getenv("DATABASE_URL", "mysql+pymysql://root:root123@localhost:3306/ecommerce_recommend"),
        },
        "crawler": {
            "url": os.getenv("DATABASE_URL", "mysql+pymysql://root:root123@localhost:3306/ecommerce_crawler"),
        },
        "analytics": {
            "url": os.getenv("DATABASE_URL", "mysql+pymysql://root:root123@localhost:3306/ecommerce_analytics"),
        },
    }

    for name, config in services.items():
        print(f"Initializing {name} database...")
        try:
            db = DatabaseManager(write_url=config["url"])
            db.init_tables()
            print(f"  {name}: OK")
        except Exception as e:
            print(f"  {name}: FAILED - {e}")


if __name__ == "__main__":
    init_all_databases()
