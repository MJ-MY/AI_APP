"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useEffect, useMemo, useState } from "react";

import { TOKEN_STORAGE_KEY } from "@/lib/auth";

type AuthUser = {
  id: string;
  email: string;
  display_name: string;
  is_active: boolean;
};

type AuthSuccess = {
  access_token: string;
  token_type: string;
  user: AuthUser;
};

type ApiError = {
  detail?: string;
};

function isApiError(value: unknown): value is ApiError {
  return (
    typeof value === "object" &&
    value !== null &&
    "detail" in value &&
    (typeof (value as { detail?: unknown }).detail === "string" ||
      typeof (value as { detail?: unknown }).detail === "undefined")
  );
}

export default function LoginPage() {
  const router = useRouter();
  const [mode, setMode] = useState<"login" | "register">("login");

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [displayName, setDisplayName] = useState("");

  const [token, setToken] = useState("");
  const [authResult, setAuthResult] = useState<AuthSuccess | null>(null);
  const [meResult, setMeResult] = useState<AuthUser | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [checkingMe, setCheckingMe] = useState(false);

  const submitLabel = useMemo(
    () => (mode === "login" ? "登录" : "注册并登录"),
    [mode],
  );

  useEffect(() => {
    const existing = window.localStorage.getItem(TOKEN_STORAGE_KEY);
    if (existing) {
      router.replace("/chat");
    }
  }, [router]);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setAuthResult(null);
    setMeResult(null);
    setLoading(true);

    try {
      const endpoint = mode === "login" ? "/api/auth/login" : "/api/auth/register";
      const body =
        mode === "login"
          ? { email, password }
          : { email, password, display_name: displayName };

      const response = await fetch(endpoint, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(body),
      });

      const data = (await response.json()) as AuthSuccess | ApiError;
      if (!response.ok) {
        setError(
          (isApiError(data) ? data.detail : undefined) ??
            "请求失败，请检查后端服务是否已启动。",
        );
        return;
      }

      const payload = data as AuthSuccess;
      setAuthResult(payload);
      setToken(payload.access_token);
      window.localStorage.setItem(TOKEN_STORAGE_KEY, payload.access_token);
      router.replace("/chat");
    } catch {
      setError("请求失败，请检查前后端服务是否已启动。");
    } finally {
      setLoading(false);
    }
  }

  async function handleCheckCurrentUser() {
    setError("");
    setMeResult(null);
    setCheckingMe(true);

    try {
      const savedToken = token || window.localStorage.getItem(TOKEN_STORAGE_KEY) || "";
      setToken(savedToken);

      if (!savedToken) {
        setError("请先登录，或者先把 access token 保存到本地。");
        return;
      }

      const response = await fetch("/api/auth/me", {
        method: "GET",
        headers: {
          Authorization: `Bearer ${savedToken}`,
        },
      });

      const data = (await response.json()) as AuthUser | ApiError;
      if (!response.ok) {
        setError((isApiError(data) ? data.detail : undefined) ?? "获取当前用户失败。");
        return;
      }

      setMeResult(data as AuthUser);
    } catch {
      setError("获取当前用户失败，请确认后端接口可用。");
    } finally {
      setCheckingMe(false);
    }
  }

  function handleLogout() {
    window.localStorage.removeItem(TOKEN_STORAGE_KEY);
    setToken("");
    setAuthResult(null);
    setMeResult(null);
    setError("");
  }

  return (
    <div className="min-h-dvh bg-zinc-50 px-6 py-10 text-zinc-950 dark:bg-black dark:text-zinc-50">
      <div className="mx-auto flex w-full max-w-5xl flex-col gap-6">
        <div className="flex items-center justify-between gap-4">
          <div>
            <h1 className="text-3xl font-semibold tracking-tight">登录模块</h1>
            <p className="mt-2 text-sm leading-6 text-zinc-600 dark:text-zinc-400">
              这里集中做注册、登录，以及测试当前登录状态。前端请求先走 Next.js
              同源接口，再转发到 FastAPI。
            </p>
          </div>
          <Link
            href="/"
            className="rounded-xl border border-zinc-200 bg-white px-4 py-2 text-sm hover:bg-zinc-100 dark:border-zinc-800 dark:bg-zinc-950 dark:hover:bg-zinc-900"
          >
            返回首页
          </Link>
        </div>

        <div className="grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
          <section className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-950">
            <div className="flex gap-2">
              <button
                type="button"
                onClick={() => setMode("login")}
                className={`rounded-xl px-4 py-2 text-sm font-medium ${
                  mode === "login"
                    ? "bg-zinc-950 text-white dark:bg-zinc-100 dark:text-zinc-950"
                    : "border border-zinc-200 bg-zinc-50 text-zinc-700 dark:border-zinc-800 dark:bg-zinc-900 dark:text-zinc-300"
                }`}
              >
                登录
              </button>
              <button
                type="button"
                onClick={() => setMode("register")}
                className={`rounded-xl px-4 py-2 text-sm font-medium ${
                  mode === "register"
                    ? "bg-zinc-950 text-white dark:bg-zinc-100 dark:text-zinc-950"
                    : "border border-zinc-200 bg-zinc-50 text-zinc-700 dark:border-zinc-800 dark:bg-zinc-900 dark:text-zinc-300"
                }`}
              >
                注册
              </button>
            </div>

            <form className="mt-6 flex flex-col gap-4" onSubmit={handleSubmit}>
              <label className="flex flex-col gap-2 text-sm">
                <span className="font-medium">邮箱</span>
                <input
                  type="email"
                  value={email}
                  onChange={(event) => setEmail(event.target.value)}
                  placeholder="请输入邮箱"
                  className="rounded-xl border border-zinc-200 bg-white px-4 py-3 outline-none ring-0 placeholder:text-zinc-400 focus:border-zinc-400 dark:border-zinc-800 dark:bg-zinc-950"
                  required
                />
              </label>

              {mode === "register" ? (
                <label className="flex flex-col gap-2 text-sm">
                  <span className="font-medium">显示名称</span>
                  <input
                    type="text"
                    value={displayName}
                    onChange={(event) => setDisplayName(event.target.value)}
                    placeholder="例如：Deng"
                    className="rounded-xl border border-zinc-200 bg-white px-4 py-3 outline-none ring-0 placeholder:text-zinc-400 focus:border-zinc-400 dark:border-zinc-800 dark:bg-zinc-950"
                    required
                  />
                </label>
              ) : null}

              <label className="flex flex-col gap-2 text-sm">
                <span className="font-medium">密码</span>
                <input
                  type="password"
                  value={password}
                  onChange={(event) => setPassword(event.target.value)}
                  placeholder="请输入密码"
                  className="rounded-xl border border-zinc-200 bg-white px-4 py-3 outline-none ring-0 placeholder:text-zinc-400 focus:border-zinc-400 dark:border-zinc-800 dark:bg-zinc-950"
                  required
                  minLength={6}
                />
              </label>

              <button
                type="submit"
                disabled={loading}
                className="mt-2 rounded-xl bg-zinc-950 px-4 py-3 text-sm font-medium text-white hover:bg-zinc-800 disabled:cursor-not-allowed disabled:opacity-60 dark:bg-zinc-100 dark:text-zinc-950 dark:hover:bg-zinc-300"
              >
                {loading ? "提交中..." : submitLabel}
              </button>
            </form>

            {error ? (
              <div className="mt-4 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700 dark:border-red-900/50 dark:bg-red-950/30 dark:text-red-300">
                {error}
              </div>
            ) : null}

            {authResult ? (
              <div className="mt-4 rounded-xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-800 dark:border-emerald-900/50 dark:bg-emerald-950/30 dark:text-emerald-300">
                {mode === "login"
                  ? "登录成功，正在进入聊天页…"
                  : "注册成功，正在进入聊天页…"}
              </div>
            ) : null}
          </section>

          <section className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-950">
            <h2 className="text-lg font-semibold">测试登录状态</h2>
            <p className="mt-2 text-sm leading-6 text-zinc-600 dark:text-zinc-400">
              登录成功后会自动把 token 存到浏览器本地。你也可以手动粘贴 token，
              然后点“测试当前用户”验证 `/api/auth/me`。
            </p>

            <label className="mt-4 flex flex-col gap-2 text-sm">
              <span className="font-medium">Access Token</span>
              <textarea
                value={token}
                onChange={(event) => setToken(event.target.value)}
                rows={6}
                placeholder="登录成功后会自动填充到这里"
                className="rounded-xl border border-zinc-200 bg-white px-4 py-3 font-mono text-xs outline-none placeholder:text-zinc-400 focus:border-zinc-400 dark:border-zinc-800 dark:bg-zinc-950"
              />
            </label>

            <div className="mt-4 flex flex-wrap gap-3">
              <button
                type="button"
                onClick={handleCheckCurrentUser}
                disabled={checkingMe}
                className="rounded-xl bg-zinc-950 px-4 py-3 text-sm font-medium text-white hover:bg-zinc-800 disabled:cursor-not-allowed disabled:opacity-60 dark:bg-zinc-100 dark:text-zinc-950 dark:hover:bg-zinc-300"
              >
                {checkingMe ? "测试中..." : "测试当前用户"}
              </button>
              <button
                type="button"
                onClick={handleLogout}
                className="rounded-xl border border-zinc-200 bg-zinc-50 px-4 py-3 text-sm hover:bg-zinc-100 dark:border-zinc-800 dark:bg-zinc-900 dark:hover:bg-zinc-800"
              >
                清空本地 Token
              </button>
            </div>

            <div className="mt-6 space-y-4">
              <div>
                <div className="text-sm font-medium">当前认证结果</div>
                <pre className="mt-2 overflow-x-auto rounded-xl border border-zinc-200 bg-zinc-50 p-4 text-xs leading-6 text-zinc-700 dark:border-zinc-800 dark:bg-zinc-900 dark:text-zinc-300">
                  {authResult ? JSON.stringify(authResult, null, 2) : "暂无数据"}
                </pre>
              </div>

              <div>
                <div className="text-sm font-medium">当前用户信息</div>
                <pre className="mt-2 overflow-x-auto rounded-xl border border-zinc-200 bg-zinc-50 p-4 text-xs leading-6 text-zinc-700 dark:border-zinc-800 dark:bg-zinc-900 dark:text-zinc-300">
                  {meResult ? JSON.stringify(meResult, null, 2) : "暂无数据"}
                </pre>
              </div>
            </div>
          </section>
        </div>
      </div>
    </div>
  );
}
