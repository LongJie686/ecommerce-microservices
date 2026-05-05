# Ecommerce Microservices -- 电商推荐系统微服务架构

基于毕设项目 [bishe](https://github.com/LongJie686/bishe)（Hadoop/Flask 单体架构）重构成 **Python + FastAPI 微服务架构**，覆盖后端笔记中 MySQL、高并发、架构设计、微服务等核心技术栈。

## 系统架构

```
                        Nginx (:80)
                      /    |    \
               gateway-service (:8001)
              /       |        \        \
         user    product   recommend  crawler  analytics
         :8002    :8003     :8004     :8005     :8006
            \       |         |         |        /
         MySQL(主从)  Redis   Kafka   共享基础设施层
```

### 6 个微服务

| 服务 | 端口 | 职责 | 核心知识点 |
|------|------|------|-----------|
| **gateway-service** | 8001 | API 网关、JWT 认证、限流、熔断 | 网关路由、令牌桶限流、Circuit Breaker |
| **user-service** | 8002 | 注册/登录/画像管理 | 表设计、复合索引、事务原子操作、逻辑删除 |
| **product-service** | 8003 | 商品 CRUD + 分类 + 搜索 | 读写分离、Redis 多级缓存、覆盖索引 |
| **recommend-service** | 8004 | 协同过滤 + 混合推荐 | CF 算法、内容推荐、AB 测试、策略模式 |
| **crawler-service** | 8005 | 异步爬虫 + 数据采集 | Kafka 生产者、Redis 分布式锁、布隆去重 |
| **analytics-service** | 8006 | 价格分布/销量趋势/店铺对比 | 聚合分析、Spark 离线计算、ECharts |

## 分层架构

每个服务统一使用三层架构，职责清晰：

```
service/
  app/
    routers/         # Controller -- API 路由，参数校验
    services/        # Service    -- 业务逻辑编排
    repositories/    # Repository -- 数据访问，SQL 封装
    models/          # Model      -- SQLAlchemy ORM 模型
    schemas/         # DTO        -- Pydantic 请求/响应模型
    config.py        # Config     -- Pydantic Settings
    main.py          # Entry      -- FastAPI 应用入口
  migrations/        # Alembic 数据库迁移
  Dockerfile
```

## 项目目录

```
ecommerce-microservices/
├── services/
│   ├── gateway/          # API 网关 (路由 + 认证 + 限流 + 熔断)
│   ├── user/             # 用户服务 (注册/登录/画像)
│   ├── product/          # 商品服务 (CRUD + 缓存 + 读写分离)
│   ├── recommend/        # 推荐服务 (CF + 混合推荐 + AB测试)
│   ├── crawler/          # 爬虫服务 (异步爬取 + Kafka)
│   └── analytics/        # 分析服务 (数据统计 + 可视化)
├── shared/               # 共享库
│   ├── database/         # MySQL 连接池 + 读写分离引擎
│   ├── cache/            # Redis 多级缓存 + 分布式锁 + 防穿透/雪崩/击穿
│   ├── mq/               # Kafka 生产者/消费者封装
│   ├── auth/             # JWT 签发/验证
│   ├── tracing/          # TraceID 链路追踪中间件
│   └── response/         # 统一响应格式
├── frontend/             # 前端页面 (Layui + ECharts)
├── deploy/
│   ├── docker-compose.yml
│   ├── nginx/nginx.conf
│   ├── mysql/
│   │   ├── master.cnf          # 主库配置 (binlog ROW)
│   │   ├── slave.cnf           # 从库配置 (read-only)
│   │   ├── init.sql            # 建库 + 复制账号
│   │   └── explain_examples.sql # EXPLAIN 分析示例
│   └── kafka/
├── scripts/
│   └── init_db.py
├── requirements.txt
└── .env.example
```

## Quick Start

```bash
# 1. 克隆仓库
git clone https://github.com/LongJie686/ecommerce-microservices.git
cd ecommerce-microservices

# 2. 配置环境变量
cp .env.example .env

# 3. 安装依赖
pip install -r requirements.txt

# 4. 启动基础设施
docker-compose -f deploy/docker-compose.yml up -d mysql-master mysql-slave redis zookeeper kafka

# 5. 初始化数据库
python scripts/init_db.py

# 6. 启动全部服务
docker-compose -f deploy/docker-compose.yml up -d
```

### 本地开发（不用 Docker 启动服务）

```bash
# 终端 1: user-service
cd services/user && PYTHONPATH=../.. uvicorn app.main:app --port 8002 --reload

# 终端 2: product-service
cd services/product && PYTHONPATH=../.. uvicorn app.main:app --port 8003 --reload

# 终端 3: recommend-service
cd services/recommend && PYTHONPATH=../.. uvicorn app.main:app --port 8004 --reload

# 终端 4: crawler-service
cd services/crawler && PYTHONPATH=../.. uvicorn app.main:app --port 8005 --reload

# 终端 5: analytics-service
cd services/analytics && PYTHONPATH=../.. uvicorn app.main:app --port 8006 --reload

# 终端 6: gateway
cd services/gateway && PYTHONPATH=../.. uvicorn app.main:app --port 8001 --reload
```

### 验证

```bash
# 健康检查
curl http://localhost:8001/health

# 注册用户
curl -X POST http://localhost:8001/api/users/register \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"123456"}'

# 登录获取 Token
curl -X POST http://localhost:8001/api/users/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"123456"}'

# 查看热门商品
curl http://localhost:8001/api/products/hot \
  -H "Authorization: Bearer <token>"

# 获取推荐
curl "http://localhost:8001/api/recommend?user_id=1&top_k=10" \
  -H "Authorization: Bearer <token>"

# 触发爬虫
curl -X POST http://localhost:8001/api/crawler/start \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"platform":"jd","keyword":"手机"}'

# 查看分析仪表盘
curl http://localhost:8001/api/analytics/dashboard \
  -H "Authorization: Bearer <token>"
```

## 技术栈

| 层 | 技术 |
|----|------|
| 框架 | FastAPI + Uvicorn |
| 数据库 | MySQL 8.0 (主从复制 + binlog ROW) |
| 缓存 | Redis 7 (多级缓存 + 分布式锁) |
| 消息队列 | Kafka + ZooKeeper |
| ORM | SQLAlchemy 2.0 (异步) |
| 迁移 | Alembic |
| 认证 | JWT (PyJWT) |
| 网关 | Nginx (反向代理 + limit_req) |
| 容器化 | Docker Compose |
| 前端 | Layui + ECharts |
| 配置 | Pydantic Settings |

## 笔记知识点覆盖

### MySQL

| 知识点 | 代码位置 | 说明 |
|--------|---------|------|
| **表设计** | `services/*/app/models/` | 字段类型选择 (DECIMAL 存金额)、NOT NULL 约束、create_time/update_time |
| **逻辑删除** | `is_deleted` 字段 | User/Product 模型 + Repository 查询过滤 |
| **复合索引** | `ix_users_username_status` | 遵循最左前缀规则，EXPLAIN 验证 |
| **覆盖索引** | `ix_products_covering_hot` | 热门商品查询只走索引不回表，EXPLAIN 显示 Using index |
| **事务** | `user_repo.create_user()` | 注册时原子写入 users + user_roles + user_profiles 三表 |
| **读写分离** | `shared/database/` | DatabaseManager 双引擎，写主库读从库 |
| **慢查询** | `deploy/mysql/master.cnf` | 开启 slow_query_log，long_query_time=1s |
| **EXPLAIN** | `deploy/mysql/explain_examples.sql` | 8 个实际查询的 EXPLAIN 分析示例 |
| **DECIMAL** | `price = Numeric(10,2)` | 金额字段用 DECIMAL 避免 FLOAT 精度丢失 |

### 高并发

| 知识点 | 代码位置 | 说明 |
|--------|---------|------|
| **多级缓存** | `shared/cache/LocalCache` | L1 进程内缓存 + L2 Redis，减少网络开销 |
| **缓存穿透** | `cache_with_anti_penetration` | 空结果缓存短 TTL，防止无效请求穿透到 DB |
| **缓存雪崩** | TTL 随机抖动 | `expire + randint(0, 60)`，避免大量 key 同时过期 |
| **缓存击穿** | `get_or_set_with_mutex` | 互斥锁模式，只允许一个请求回源 DB |
| **分布式锁** | `acquire/release_lock` | Lua 脚本安全释放 (验证 owner)，防止误删 |
| **熔断降级** | `gateway/CircuitBreaker` | 三态机 (CLOSED/OPEN/HALF_OPEN)，连续 5 次失败触发熔断 |
| **限流** | gateway Lua + Nginx | 原子 INCR 滑动窗口 + Nginx limit_req 30r/s |
| **链路追踪** | `shared/tracing` | X-Trace-ID 全链路透传，Nginx -> Gateway -> Service |

### 架构设计

| 知识点 | 代码位置 | 说明 |
|--------|---------|------|
| **分层架构** | `routers/ -> services/ -> repositories/` | Controller/Service/Repository 三层分离 |
| **微服务拆分** | 6 个独立服务 | 按业务域拆分，独立数据库，独立部署 |
| **API 网关** | gateway-service | 统一入口：路由 + 认证 + 限流 + 熔断 |
| **消息队列** | crawler -> Kafka -> analytics | 异步解耦，爬虫结果通过 Kafka 推送 |
| **策略模式** | `recommend/algorithms/` | CF/ContentBased/Hot/Hybrid 可插拔推荐算法 |
| **统一响应** | `shared/response/` | success() / error() / paginated() 标准格式 |
| **配置管理** | Pydantic Settings | 环境变量注入，.env 文件支持 |

### 微服务

| 知识点 | 代码位置 | 说明 |
|--------|---------|------|
| **服务注册** | `SERVICE_MAP` | 网关静态路由表，按前缀匹配转发 |
| **服务通信** | httpx AsyncClient | 同步 HTTP 调用 (网关 -> 服务)，超时 10s |
| **异步通信** | Kafka Topic | crawler 生产 -> analytics 消费 |
| **数据隔离** | 每服务独立数据库 | ecommerce_user/product/recommend/crawler/analytics |
| **Docker 部署** | docker-compose.yml | 一键启动全栈 (MySQL 主从 + Redis + Kafka + 6 服务 + Nginx) |

## License

MIT
