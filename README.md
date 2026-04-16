# AI_APP

前后端分离骨架：

- `frontend/`: Next.js（页面 + 同源网关转发 `/api/*`）
- `backend/`: FastAPI（业务后端：后续接 MiniMax / RAG / 知识库）

## 本地运行（不需要 Docker）

### 1) 启动后端（FastAPI）

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 配置环境变量（先不配也能跑 health）
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

