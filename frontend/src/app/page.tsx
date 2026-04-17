export default function Home() {
  return (
    <div className="flex min-h-dvh flex-col items-center justify-center bg-zinc-50 px-6 font-sans text-zinc-950 dark:bg-black dark:text-zinc-50">
      <main className="w-full max-w-3xl rounded-2xl border border-zinc-200 bg-white p-8 shadow-sm dark:border-zinc-800 dark:bg-zinc-950">
        <div className="flex flex-col gap-2">
          <h1 className="text-2xl font-semibold tracking-tight">AI Agent App</h1>
          <p className="text-sm leading-6 text-zinc-600 dark:text-zinc-400">
            Next.js 作为网关转发（同源 API），FastAPI 作为业务后端（后续接
            MiniMax / RAG / 知识库）。
          </p>
        </div>

        <div className="mt-6 grid gap-3">
          <a
            className="rounded-xl border border-zinc-200 bg-zinc-50 px-4 py-3 text-sm hover:bg-zinc-100 dark:border-zinc-800 dark:bg-zinc-900 dark:hover:bg-zinc-800"
            href="/login"
          >
            打开 <code className="font-mono">/login</code>（前端登录/注册/测试登录页）
          </a>
          <a
            className="rounded-xl border border-zinc-200 bg-zinc-50 px-4 py-3 text-sm hover:bg-zinc-100 dark:border-zinc-800 dark:bg-zinc-900 dark:hover:bg-zinc-800"
            href="/chat"
          >
            打开 <code className="font-mono">/chat</code>（需已登录，否则会自动跳转到登录页）
          </a>
          <a
            className="rounded-xl border border-zinc-200 bg-zinc-50 px-4 py-3 text-sm hover:bg-zinc-100 dark:border-zinc-800 dark:bg-zinc-900 dark:hover:bg-zinc-800"
            href="/api/health"
            target="_blank"
            rel="noreferrer"
          >
            打开 <code className="font-mono">/api/health</code>（验证：Next → FastAPI
            转发）
          </a>
          <div className="rounded-xl border border-zinc-200 px-4 py-3 text-sm dark:border-zinc-800">
            <div className="font-medium">下一步你可以做：</div>
            <ul className="mt-2 list-disc space-y-1 pl-5 text-zinc-700 dark:text-zinc-300">
              <li>
                在 FastAPI 增加 <code className="font-mono">/v1/chat/stream</code>，
                并用 MiniMax key 调通流式输出
              </li>
              <li>前端新增 Chat 页面，接入流式渲染 + 停止生成</li>
              <li>再加文档上传（直传 FastAPI）→ 解析 → pgvector → RAG</li>
            </ul>
          </div>
        </div>
      </main>
    </div>
  );
}
