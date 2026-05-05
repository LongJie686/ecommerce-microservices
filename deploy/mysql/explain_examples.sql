-- ============================================================
-- EXPLAIN Analysis Examples for ecommerce-microservices
-- Demonstrates index usage, covering index, and query optimization
-- ============================================================

-- 1. Composite index: username + status
-- Index: ix_users_username_status (username, status)
EXPLAIN SELECT * FROM users WHERE username = 'admin' AND status = 1;
-- Expected: type=ref, key=ix_users_username_status (uses composite index)

-- Compare with no index on single column that isn't leading:
EXPLAIN SELECT * FROM users WHERE status = 1;
-- Expected: type=ALL or type=ref (full scan or uses single index, less efficient)

-- 2. Logical deletion with composite index
-- Filter is_deleted=0 should leverage composite index
EXPLAIN SELECT id, username, nickname FROM users WHERE username = 'test' AND is_deleted = 0 AND status = 1;
-- Expected: type=ref, key=ix_users_username_status, Extra: Using where

-- 3. Covering index on products: hot list query
-- Index: ix_products_covering_hot (status, sales_count, name, price)
EXPLAIN SELECT name, price, sales_count FROM products
WHERE status = 1 AND is_deleted = 0
ORDER BY sales_count DESC LIMIT 20;
-- Expected: type=ref, key=ix_products_covering_hot, Extra: Using index (covering!)
-- "Using index" means MySQL reads ONLY the index, no table lookup needed

-- Compare WITHOUT covering index (selects columns not in the index):
EXPLAIN SELECT id, name, price, sales_count, description FROM products
WHERE status = 1 AND is_deleted = 0
ORDER BY sales_count DESC LIMIT 20;
-- Expected: Extra does NOT show "Using index" because description is not in index

-- 4. Composite index: category_id + status for product listing
-- Index: ix_products_category_status (category_id, status)
EXPLAIN SELECT * FROM products
WHERE category_id = 5 AND status = 1 AND is_deleted = 0
ORDER BY sales_count DESC LIMIT 20;
-- Expected: type=ref, key=ix_products_category_status

-- 5. Range query on price with index
-- Index: ix_products_price (price)
EXPLAIN SELECT * FROM products WHERE price BETWEEN 100 AND 500 AND status = 1 AND is_deleted = 0;
-- Expected: type=range, key=ix_products_price

-- 6. Full table scan example (what NOT to do)
EXPLAIN SELECT * FROM products WHERE description LIKE '%手机%';
-- Expected: type=ALL, Extra: Using where (no index can help LIKE '%...%')

-- 7. Crawl task status query
-- Index: ix_crawl_task_status (status)
EXPLAIN SELECT * FROM crawl_tasks WHERE status = 'running';
-- Expected: type=ref, key=ix_crawl_task_status

-- 8. User behavior query for recommendations
-- With composite index on (user_id, behavior_type)
EXPLAIN SELECT * FROM user_behaviors WHERE user_id = 1 AND behavior_type = 'purchase' ORDER BY created_at DESC LIMIT 20;
-- Expected: type=ref, uses composite index on user_id + behavior_type

-- ============================================================
-- Index Design Principles Demonstrated in This Project:
--
-- 1. Composite Index Leftmost Prefix Rule:
--    INDEX(a, b, c) can serve queries on (a), (a,b), (a,b,c)
--    but NOT (b), (c), or (b,c) alone
--
-- 2. Covering Index (覆盖索引):
--    All columns needed by the query are in the index itself.
--    MySQL reads only the B+ tree leaf nodes, skips table lookup.
--    Look for "Using index" in EXPLAIN Extra column.
--
-- 3. Logical Deletion (逻辑删除):
--    is_deleted=0 filter added to all queries.
--    Ensures "deleted" records are invisible but preserved for audit.
--
-- 4. DECIMAL for Money:
--    price DECIMAL(10,2) avoids floating-point precision issues.
--    NEVER use FLOAT/DOUBLE for monetary values.
-- ============================================================
