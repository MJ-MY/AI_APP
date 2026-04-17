# AI_APP

前后端分离骨架：

- `frontend/`: Next.js（页面 + 同源网关转发 `/api/*`）
- `backend/`: FastAPI（业务后端：后续接 MiniMax / RAG / 知识库）

## 本地 Postgres（注册登录需要数据库）

如果你看到注册接口报错类似 `connection refused` 到 `127.0.0.1:5432`，说明本机 Postgres 没启动。

在项目根目录执行：

```bash
docker compose up -d postgres
```

默认会启动一个 Postgres（账号/密码/库名都是 `ai_app`），并映射到本机 `5432`。

你也可以参考：

- `docker-compose.yml`
- `backend/.env.example`

## 本地运行（不需要 Docker）

### 1) 启动后端（FastAPI）

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 配置环境变量（注册登录建议至少配置 DATABASE_URL / JWT_SECRET）
# 推荐做法：复制 backend/.env.example 为 backend/.env.local 再按需修改
export MINIMAX_API_KEY="你的key"

uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

打开：

- `http://127.0.0.1:8000/health`

### 2) 启动前端（Next.js）

```bash
cd frontend
npm install

# 可选：复制环境变量
# cp .env.example .env.local
# 然后按需修改 BACKEND_URL

npm run dev
```

打开：

- `http://localhost:3000/`
- `http://localhost:3000/api/health`（验证：Next.js → FastAPI 转发）

## 下一步（你后续要加的内容）

- FastAPI：把 `POST /v1/chat/stream` 替换为 MiniMax 流式调用
- Next.js：新增 Chat 页面，接 `/api/chat/stream` 并做流式渲染 + 停止生成
- 再加文件上传（浏览器直传 FastAPI）→ 文档解析 → pgvector → RAG

