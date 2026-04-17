# 登录与注册（本地开发说明）

本文说明：从浏览器点击注册/登录，到数据写入 Postgres，再到拿到 `access_token` 的完整链路，以及本地依赖（Docker / Postgres / FastAPI / Next.js）分别负责什么。

## 组件与职责

- **浏览器**：访问前端页面，发起 `fetch` 请求。
- **Next.js（前端）**：提供 UI（`/login`），并通过同源 API Route 作为网关转发到后端。
- **FastAPI（后端）**：实现 `/v1/auth/register`、`/v1/auth/login`、`/v1/auth/me`，做校验、写库、签发 JWT。
- **PostgreSQL（数据库）**：持久化保存用户表 `users`。
- **Docker Desktop + Docker Compose**：在本机拉起 Postgres 容器（可选，但推荐）。

## 端到端请求链路（注册为例）

1. 打开页面：`http://localhost:3000/login`
2. 浏览器请求（同源）：`POST /api/auth/register`
3. Next.js Route Handler 转发：`POST http://127.0.0.1:8000/v1/auth/register`
4. FastAPI：
   - 校验请求体（邮箱/密码/昵称）
   - 检查邮箱是否已存在
   - 对密码做 **bcrypt** 哈希后写入 `users`
   - 签发 JWT（`access_token`）
5. 返回 JSON 给前端，前端把 token 存到 `localStorage`（当前实现）

登录同理，只是调用 `/api/auth/login` → `/v1/auth/login`。

## 关键文件位置

### 前端

- 登录页：`frontend/src/app/login/page.tsx`
- 网关转发：
  - `frontend/src/app/api/auth/register/route.ts`
  - `frontend/src/app/api/auth/login/route.ts`
  - `frontend/src/app/api/auth/me/route.ts`

### 后端

- 入口与路由：`backend/app/main.py`
- 用户模型：`backend/app/models.py`
- 请求/响应模型：`backend/app/schemas.py`
- JWT 与密码哈希：`backend/app/auth.py`
- 当前用户依赖：`backend/app/dependencies.py`
- 数据库连接：`backend/app/db.py`
- 配置：`backend/app/config.py`

## 环境变量（你需要配置什么）

### 前端

- `frontend/.env.local`（从 `frontend/.env.example` 复制）
  - `BACKEND_URL`：默认 `http://127.0.0.1:8000`

### 后端

建议把敏感信息放在本地文件（不要提交到 git）：

- `backend/.env.local` 或 `backend/app/.env.local`

至少需要：

- `DATABASE_URL`：例如 `postgresql+psycopg://ai_app:ai_app@127.0.0.1:5432/ai_app`
- `JWT_SECRET`：足够长的随机字符串
- `MINIMAX_API_KEY`：仅在你开始接模型时需要（与登录注册无强依赖）

示例模板见：`backend/.env.example`

## 用 Docker Compose 启动 Postgres（推荐）

在项目根目录（包含 `docker-compose.yml`）执行：

```bash
cd /Users/dengminjian/Desktop/AI_APP
docker compose up -d postgres
docker compose ps
```

默认会创建：

- 容器名：`ai_app_postgres`
- 端口映射：`5432:5432`
- 用户/密码/库名：`ai_app / ai_app / ai_app`

> 注意：如果你无法从本机访问 Docker Hub 拉镜像，需要先解决网络/镜像加速/代理问题，否则 `docker compose up` 会失败。

## 本地启动顺序（最常见）

1. 启动 Postgres（Docker Compose 或本机安装 Postgres 均可）
2. 启动后端：

```bash
cd backend
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

3. 启动前端：

```bash
cd frontend
npm install
npm run dev
```

4. 打开 `http://localhost:3000/login` 注册/登录

## 常见问题排查（你这次踩过的）

### 1）`503` 提示数据库连接失败

含义：FastAPI 连不上 `DATABASE_URL` 指向的 Postgres（常见是 Postgres 没启动、端口不对、账号密码不对）。

处理：

- 确认 Postgres 已启动且 `5432` 可连
- 修改 `DATABASE_URL` 与实际账号一致
- 后端修改环境变量后建议重启 `uvicorn`

### 2）注册 `500`，日志里出现 bcrypt / passlib 相关错误

含义：历史上 `passlib` 与较新的 `bcrypt` 版本组合可能不兼容，导致密码哈希阶段异常。

处理原则：

- 使用稳定的 `bcrypt` 版本，并避免旧的 `passlib` 组合踩坑
- 重新安装依赖并重启后端

### 3）Docker Desktop 显示 Engine running，但拉镜像超时

含义：Docker Engine 正常，但访问镜像仓库网络不通（DNS/代理/防火墙/地区网络等）。

处理：

- 先验证本机能否访问镜像仓库（用 `curl` 或浏览器）
- 配置可用的网络出口（热点/VPN/公司代理）
- 或在 Docker Desktop 配置镜像加速（取决于你网络环境是否可用）

## 安全提醒（很重要）

- **不要把真实 API Key 写进会被提交的仓库文件**。
- 任何密钥一旦出现在聊天/截图/日志里，都建议去对应平台 **轮换（revoke + 重新生成）**。
