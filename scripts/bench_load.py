"""
Ecommerce Microservices Load Test v3
Starts services, lets ORM create tables, seeds via API, runs benchmarks.
"""
import json
import os
import sys
import time
import statistics
import subprocess
import threading
import pymysql
from concurrent.futures import ThreadPoolExecutor
from urllib.request import Request, urlopen
from urllib.error import URLError

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MYSQL_PASS = os.getenv("MYSQL_ROOT_PASSWORD", "root123")


def http_req(url, data=None, headers=None, timeout=10):
    body = json.dumps(data).encode() if data else None
    req = Request(url, data=body, method="POST" if data else "GET")
    req.add_header("Content-Type", "application/json")
    if headers:
        for k, v in headers.items():
            req.add_header(k, v)
    t0 = time.time()
    try:
        resp = urlopen(req, timeout=timeout)
        return resp.status, json.loads(resp.read()), time.time() - t0
    except URLError as e:
        code = getattr(e, "code", 0)
        try:
            rbody = json.loads(e.read())
        except Exception:
            rbody = {"error": str(e)}
        return code, rbody, time.time() - t0
    except Exception as e:
        return 0, {"error": str(e)}, time.time() - t0


def reset_databases():
    """Drop and recreate databases."""
    conn = pymysql.connect(host="localhost", port=3306, user="root", password=MYSQL_PASS, charset="utf8mb4")
    cur = conn.cursor()
    for db in ["ecommerce_user", "ecommerce_product", "ecommerce_recommend",
               "ecommerce_crawler", "ecommerce_analytics"]:
        cur.execute(f"DROP DATABASE IF EXISTS `{db}`")
        cur.execute(f"CREATE DATABASE `{db}` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
    conn.close()
    print("  Databases reset.")


def start_service(name, port, cwd_rel, env_extra):
    cwd = os.path.join(BASE, cwd_rel)
    env = os.environ.copy()
    env["PYTHONPATH"] = f"{BASE}{os.pathsep}{cwd}"
    env["DATABASE_URL"] = f"mysql+pymysql://root:{MYSQL_PASS}@localhost:3306/ecommerce_{name if name != 'gateway' else 'user'}"
    env["REDIS_URL"] = "redis://localhost:6379/0"
    env["JWT_SECRET"] = os.getenv("JWT_SECRET", "bench-test-secret-key-32-characters")
    env.update(env_extra)

    p = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app",
         "--host", "0.0.0.0", "--port", str(port), "--no-access-log"],
        cwd=cwd, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
    )

    for attempt in range(30):
        time.sleep(0.5)
        try:
            resp = urlopen(f"http://localhost:{port}/health", timeout=2)
            if resp.status == 200:
                print(f"  [OK] {name} :{port} (PID {p.pid})")
                return p
        except Exception:
            pass

    err = p.stderr.read().decode()[-400:] if p.stderr else ""
    print(f"  [FAIL] {name}: {err}")
    p.kill()
    return None


def seed_data(token):
    """Register users and insert products via raw SQL."""
    auth = {"Authorization": f"Bearer {token}"}

    # Register 100 users via API
    print("  Registering users...")
    for i in range(100):
        http_req("http://localhost:8002/api/users/register",
                 {"username": f"bench_user_{i}", "password": "test123"})

    conn = pymysql.connect(host="localhost", port=3306, user="root",
                           password=MYSQL_PASS, database="ecommerce_product", charset="utf8mb4")
    cur = conn.cursor()

    # Insert categories
    categories = ["手机", "电脑", "耳机", "平板", "相机", "手表", "音箱", "键盘", "显示器", "路由器"]
    cat_rows = [(c, i) for i, c in enumerate(categories)]
    cur.executemany("INSERT INTO categories (name, sort_order) VALUES (%s, %s)", cat_rows)
    conn.commit()

    # Insert products matching ORM schema
    import random
    brands = ["华为", "小米", "苹果", "三星", "索尼", "联想", "OPPO", "vivo", "荣耀", "一加"]

    batch = []
    for i in range(1, 5001):
        cat_id = random.randint(1, len(categories))
        brand = random.choice(brands)
        cat_name = categories[cat_id - 1]
        price = round(random.uniform(99, 9999), 2)
        batch.append((f"{brand}{cat_name}型号{i}", cat_id, price,
                       round(price * random.uniform(1.1, 1.5), 2),
                       f"{brand}品牌{cat_name}，型号{i}",
                       "", random.randint(0, 50000),
                       round(random.uniform(3.0, 5.0), 1),
                       random.choice(["jd", "taobao"]),
                       f"https://example.com/item/{i}"))
    cur.executemany("""INSERT INTO products
        (name, category_id, price, original_price, description, image_url,
         sales_count, rating, source, source_url, is_deleted, status) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,0,1)""", batch)
    conn.commit()
    print(f"  Products: {cur.rowcount} rows")
    conn.close()

    # Seed behaviors
    print("  Seeding behaviors...")
    conn = pymysql.connect(host="localhost", port=3306, user="root",
                           password=MYSQL_PASS, database="ecommerce_recommend", charset="utf8mb4")
    cur = conn.cursor()
    actions = ["view", "click", "purchase", "favorite"]
    behaviors = []
    for uid in range(1, 101):
        for _ in range(random.randint(10, 25)):
            action = random.choice(actions)
            score = {"view": 1.0, "click": 2.0, "favorite": 3.0, "purchase": 5.0}[action]
            behaviors.append((uid, random.randint(1, 5000), action, score))
    cur.executemany("INSERT INTO user_behaviors (user_id, product_id, behavior_type, score) VALUES (%s,%s,%s,%s)", behaviors)
    conn.commit()
    print(f"  Behaviors: {cur.rowcount} rows")
    conn.close()
    print("  Seeding complete.")


def run_benchmark(name, func, total=2000, concurrent=50):
    latencies = []
    errors = 0
    lock = threading.Lock()

    def worker():
        nonlocal errors
        try:
            status, _, elapsed = func()
            with lock:
                latencies.append(elapsed)
                if status >= 400:
                    errors += 1
        except Exception:
            with lock:
                latencies.append(10.0)
                errors += 1

    t_start = time.time()
    with ThreadPoolExecutor(max_workers=concurrent) as pool:
        for _ in range(total):
            pool.submit(worker)
    t_total = time.time() - t_start

    if not latencies:
        print(f"  [{name}] No responses!")
        return None

    latencies.sort()
    n = len(latencies)
    qps = n / t_total
    avg = statistics.mean(latencies)
    p50 = latencies[int(n * 0.5)]
    p90 = latencies[int(n * 0.9)]
    p99 = latencies[int(n * 0.99)]
    err_rate = errors / n * 100

    print(f"  [{name}] {n} req | QPS: {qps:.0f} | "
          f"Avg: {avg*1000:.1f}ms | P50: {p50*1000:.1f}ms | "
          f"P90: {p90*1000:.1f}ms | P99: {p99*1000:.1f}ms | "
          f"Err: {err_rate:.1f}%")
    return {"name": name, "qps": qps, "avg_ms": avg*1000,
            "p50_ms": p50*1000, "p90_ms": p90*1000, "p99_ms": p99*1000,
            "err_rate": err_rate, "total": n}


def main():
    print("=" * 60)
    print("  Ecommerce Microservices Load Test v3")
    print("=" * 60)

    # 1. Reset DBs
    print("\n[1/5] Resetting databases...")
    reset_databases()

    # 2. Start services (ORM creates tables)
    print("\n[2/5] Starting services...")
    p_user = start_service("user", 8002, "services/user", {})
    p_prod = start_service("product", 8003, "services/product", {"REDIS_URL": "redis://localhost:6379/1"})
    p_rec = start_service("recommend", 8004, "services/recommend", {"REDIS_URL": "redis://localhost:6379/2"})
    p_gw = start_service("gateway", 8001, "services/gateway", {
        "USER_SERVICE_URL": "http://localhost:8002",
        "PRODUCT_SERVICE_URL": "http://localhost:8003",
        "RECOMMEND_SERVICE_URL": "http://localhost:8004",
        "CRAWLER_SERVICE_URL": "http://localhost:8005",
        "ANALYTICS_SERVICE_URL": "http://localhost:8006",
    })
    procs = [p for p in [p_user, p_prod, p_rec, p_gw] if p]
    if len(procs) < 4:
        print("  Aborting."); [p.kill() for p in procs]; return

    # 3. Register + login
    print("\n[3/5] Registering and logging in...")
    http_req("http://localhost:8002/api/users/register",
             {"username": "bench_user_0", "password": "test123"})
    status, body, _ = http_req("http://localhost:8002/api/users/login",
                               {"username": "bench_user_0", "password": "test123"})
    token = body.get("data", {}).get("token")
    print(f"  Token: {'OK' if token else 'FAIL'}")
    if not token:
        print(f"  Response: {body}")
        [p.kill() for p in procs]; return
    auth = {"Authorization": f"Bearer {token}"}

    # 4. Seed data
    print("\n[4/5] Seeding data...")
    seed_data(token)

    # Warmup
    for _ in range(30):
        http_req("http://localhost:8003/api/products?page=1&page_size=20", headers=auth)

    # 5. Benchmarks
    print(f"\n[5/5] Running benchmarks...")
    print("-" * 60)
    results = []

    r = run_benchmark("Login", lambda: http_req(
        "http://localhost:8002/api/users/login",
        {"username": "bench_user_0", "password": "test123"}
    ), total=500, concurrent=30)
    if r: results.append(r)

    r = run_benchmark("Product List", lambda: http_req(
        "http://localhost:8003/api/products?page=1&page_size=20", headers=auth
    ))
    if r: results.append(r)

    r = run_benchmark("Product Detail", lambda: http_req(
        "http://localhost:8003/api/products/1", headers=auth
    ))
    if r: results.append(r)

    r = run_benchmark("Search", lambda: http_req(
        "http://localhost:8003/api/search?keyword=手机&page=1&page_size=20", headers=auth
    ), total=1000)
    if r: results.append(r)

    r = run_benchmark("Hot Products", lambda: http_req(
        "http://localhost:8003/api/products/hot?limit=20", headers=auth
    ))
    if r: results.append(r)

    r = run_benchmark("Gateway->Products", lambda: http_req(
        "http://localhost:8001/api/products?page=1&page_size=20", headers=auth
    ), total=1000)
    if r: results.append(r)

    r = run_benchmark("Recommend", lambda: http_req(
        "http://localhost:8004/api/recommend/bench_user_0?top_k=10", headers=auth
    ), total=500)
    if r: results.append(r)

    # Summary
    print("\n" + "=" * 60)
    print("  SUMMARY")
    print("=" * 60)
    print(f"  {'Scenario':<20} {'QPS':>6} {'Avg':>8} {'P50':>8} {'P90':>8} {'P99':>8} {'Err%':>6}")
    print(f"  {'':-<20} {'':->6} {'':->8} {'':->8} {'':->8} {'':->8} {'':->6}")
    for r in results:
        print(f"  {r['name']:<20} {r['qps']:>6.0f} {r['avg_ms']:>7.1f}ms "
              f"{r['p50_ms']:>7.1f}ms {r['p90_ms']:>7.1f}ms {r['p99_ms']:>7.1f}ms "
              f"{r['err_rate']:>5.1f}%")

    if results:
        print(f"\n  Peak QPS: {max(r['qps'] for r in results):.0f}")
        print(f"  Avg QPS: {statistics.mean([r['qps'] for r in results]):.0f}")
        print(f"  Avg P90: {statistics.mean([r['p90_ms'] for r in results]):.1f}ms")

    print("\n  Stopping services...")
    for p in procs:
        p.kill()
    print("  Done.")


if __name__ == "__main__":
    main()
