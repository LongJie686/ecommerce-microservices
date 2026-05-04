# Ecommerce Microservices

基于 Hadoop 的淘宝商品智能推荐系统 -- 微服务重构版。

基于毕设项目 [bishe](https://github.com/LongJie686/bishe) 重构，用 Python + FastAPI 微服务架构实现，体现笔记中的 MySQL、高并发、架构设计、微服务等技术栈。

## 微服务架构

```
Nginx (:80) → gateway-service (:8001) → 5 个业务服务 → MySQL + Redis + Kafka
```

| 服务 | 端口 | 职责 | 体现的知识点 |
|------|------|------|-------------|
| gateway-service | 8001 | API 网关、认证、限流 | 微服务网关、高并发限流 |
| user-service | 8002 | 用户注册/登录/画像 | MySQL 表设计、索引、事务 |
| product-service | 8003 | 商品 CRUD + 搜索 | MySQL 读写分离、Redis 缓存 |
| recommend-service | 8004 | 推荐算法 | 协同过滤、混合推荐、AB测试 |
| crawler-service | 8005 | 数据采集 | Kafka 消息队列、异步爬虫 |
| analytics-service | 8006 | 数据分析可视化 | Spark 离线分析、ECharts |

## 分层架构

每个服务统一使用 Controller → Service → Repository 三层：

```
service/
  app/
    routers/         # Controller: API 路由
    services/        # Service: 业务逻辑
    repositories/    # Repository: 数据访问
    models/          # Model: ORM 模型
    schemas/         # DTO: 请求/响应模型
```

## Quick Start

```bash
git clone https://github.com/LongJie686/ecommerce-microservices.git
cd ecommerce-microservices
cp .env.example .env

# 启动基础设施
docker-compose -f deploy/docker-compose.yml up -d mysql-master mysql-slave redis zookeeper kafka

# 初始化数据库
python scripts/init_db.py

# 启动服务
docker-compose -f deploy/docker-compose.yml up -d
```

## 技术栈

| 层 | 技术 |
|----|------|
| 框架 | FastAPI + Uvicorn |
| 数据库 | MySQL 8.0 (主从复制) |
| 缓存 | Redis 7 |
| 消息队列 | Kafka + ZooKeeper |
| ORM | SQLAlchemy 2.0 |
| 迁移 | Alembic |
| 认证 | JWT |
| 网关 | Nginx |
| 容器化 | Docker Compose |

## 笔记知识点覆盖

| 笔记领域 | 项目体现 |
|---------|---------|
| MySQL 表设计 | 3 个独立数据库，字段类型选择、主键设计、反范式 |
| MySQL 索引 | 复合索引、覆盖索引、EXPLAIN 分析示例 |
| MySQL 事务 | 用户注册原子操作 |
| MySQL 读写分离 | product-service 读写路由到主/从库 |
| Redis 缓存 | 热点商品缓存、缓存穿透/雪崩防护 |
| 高并发限流 | gateway 令牌桶 + Nginx limit_req |
| 消息队列 | Kafka 爬虫结果推送 + 用户行为事件 |
| 分层架构 | Controller → Service → Repository |
| 微服务拆分 | 6 个独立服务 |
| API 网关 | Nginx + gateway-service |
| 链路追踪 | TraceID 全链路透传 |
| Docker | docker-compose 一键启动 |

## License

MIT
