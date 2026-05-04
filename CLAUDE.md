# CLAUDE.md

## 项目概述

电商推荐系统微服务架构项目，基于 Python + FastAPI。

## 架构

- 6 个微服务：gateway、user、product、recommend、crawler、analytics
- 每个服务独立数据库（MySQL），共享 Redis 和 Kafka
- Nginx 反向代理 + gateway-service 统一入口

## 分层规范

每个服务必须遵循三层架构：
- `routers/` -- Controller，只做参数校验和响应格式化
- `services/` -- 业务逻辑，不依赖 FastAPI
- `repositories/` -- 数据访问，封装 SQL

## 关键约束

- API 响应统一使用 `shared.response` 的 `success()` / `paginated()` / `error()`
- 数据库操作用 `shared.database.DatabaseManager`，支持读写分离
- 缓存用 `shared.cache.RedisClient`，带防穿透/雪崩
- 所有请求必须带 TraceID（`shared.tracing.TracingMiddleware`）
- 每个服务有独立的 `config.py`（Pydantic Settings）

## 常用命令

```bash
# 启动基础设施
docker-compose -f deploy/docker-compose.yml up -d

# 运行单个服务（开发模式）
cd services/user && uvicorn app.main:app --reload --port 8002

# 数据库迁移
cd services/user && alembic upgrade head

# 运行测试
pytest services/user/tests/ -v
```
