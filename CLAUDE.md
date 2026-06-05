# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

电商推荐系统微服务架构，基于 Python + FastAPI + SQLAlchemy + MySQL + Redis + Kafka。

## 服务端口映射

| 服务 | 端口 | 数据库 | Redis DB |
|------|------|--------|----------|
| gateway | 8001 | ecommerce | 0 |
| user | 8002 | ecommerce_user | - |
| product | 8003 | ecommerce_product | 1 |
| recommend | 8004 | ecommerce_recommend | 2 |
| crawler | 8005 | ecommerce_crawler | 3 |
| analytics | 8006 | ecommerce_analytics | - |

基础设施：MySQL master:3306 / slave:3307，Redis:6379，Kafka:9092。

## 常用命令

```bash
# 启动基础设施（MySQL主从 + Redis + Kafka）
docker-compose -f deploy/docker-compose.yml up -d

# 运行单个服务（开发模式）
cd services/user && uvicorn app.main:app --reload --port 8002

# 数据库迁移（每个服务独立执行）
cd services/user && alembic upgrade head

# 运行测试
pytest services/user/tests/ -v
pytest services/user/tests/ -v -k "test_login"  # 运行单个测试

# 代码格式化与检查
black services/ shared/
ruff check services/ shared/
```

## 分层架构（每个服务强制三层）

```
services/<name>/app/
  main.py          # FastAPI app + lifespan（连接 DB/Redis，init_tables）
  config.py        # Pydantic Settings，从环境变量或 .env 读取
  routers/         # Controller：仅做参数校验 + 调用 Service，通过 Depends 注入 Session
  services/        # 业务逻辑：纯 Python，不依赖 FastAPI
  repositories/    # 数据访问：封装 SQL，通过 Session 操作 ORM
  models/          # SQLAlchemy ORM 模型
  schemas/         # Pydantic 请求/响应 Schema
```

## shared 库

| 模块 | 用途 |
|------|------|
| `shared.auth` | JWT 创建（`create_token`）和验证（`verify_token`），HS256 |
| `shared.database.DatabaseManager` | SQLAlchemy 连接池，读写分离；`get_write_session()` / `get_read_session()` 作为 Depends |
| `shared.cache.RedisClient` | 两级缓存（L1 进程内 + L2 Redis），防穿透/击穿/雪崩 |
| `shared.response` | 统一响应：`success()` / `error()` / `paginated()` |
| `shared.tracing.TracingMiddleware` | 注入 X-Trace-ID，所有服务均需 `app.add_middleware(TracingMiddleware)` |
| `shared.mq` | aiokafka 封装：`KafkaProducer` / `KafkaConsumer` |

## Gateway 机制

- **路由表**：`SERVICE_MAP` 按路径前缀（`/api/users`, `/api/products` 等）转发到各服务。
- **公开路径**（无需 JWT）：`/health`, `/api/users/login`, `/api/users/register`。
- **限流**：Redis Lua 滑动窗口，默认 60 RPM（`settings.rate_limit_rpm`），key 为 `rate:<X-Trace-ID>`。
- **熔断器**：`CircuitBreaker`，5次失败后 OPEN，30秒后进入 HALF_OPEN 探测。
- **代理**：用 `httpx.AsyncClient` 转发，超时 10s；5xx 响应计入熔断失败次数。

## 关键开发约定

**新增服务端点：**
1. 在 `schemas/` 定义 Pydantic 输入/输出模型
2. 在 `repositories/` 封装 SQL 操作（传入 `Session`，不持有连接）
3. 在 `services/` 实现业务逻辑（调用 repo，返回 `shared.response` 格式的 dict）
4. 在 `routers/` 注册路由，通过 `Depends(get_write_session)` 或 `Depends(get_read_session)` 注入 Session

**缓存使用模式：**
- 防穿透：`cache_with_anti_penetration` / `get_with_anti_penetration`（null 占位 60s）
- 防击穿：`get_or_set_with_mutex`（互斥锁 + double-check）
- 多级缓存：`get_multi_level` / `set_multi_level`（L1 TTL=30s，L2 按配置）

**lifespan 模式：**
```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    from app.models.xxx import ModelClass  # 触发 ORM 注册
    db.init_tables()
    await redis.connect()
    yield
    await redis.close()
```

**读写分离：**
- 写操作（INSERT/UPDATE/DELETE）用 `get_write_session`
- 读操作（SELECT）用 `get_read_session`
- `read_database_url` 未配置时自动回退到 write 连接
