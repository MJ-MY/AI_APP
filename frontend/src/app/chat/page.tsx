"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { TOKEN_STORAGE_KEY } from "@/lib/auth";

type AuthUser = {
  id: string;
  email: string;
  display_name: string;
  is_active: boolean;
};

type ApiError = { detail?: string };

function isApiError(value: unknown): value is ApiError {
  return (
    typeof value === "object" &&
    value !== null &&
    "detail" in value &&
    (typeof (value as { detail?: unknown }).detail === "string" ||
      typeof (value as { detail?: unknown }).detail === "undefined")
  );
}

export default function ChatPage() {
  const router = useRouter();
  const [user, setUser] = useState<AuthUser | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = window.localStorage.getItem(TOKEN_STORAGE_KEY);
    if (!token) {
      router.replace("/login");
      return;
    }

    let cancelled = false;

    (async () => {
      setLoading(true);
      setError("");
      try {
        const response = await fetch("/api/auth/me", {
          headers: { Authorization: `Bearer ${token}` },
        });
        const data = (await response.json()) as AuthUser | ApiError;
        if (!response.ok) {
          if (!cancelled) {
            setError(
              (isApiError(data) ? data.detail : undefined) ??
                "登录已失效，请重新登录。",
            );
            window.localStorage.removeItem(TOKEN_STORAGE_KEY);
            router.replace("/login");
          }
          return;
        }
        if (!cancelled) {
          setUser(data as AuthUser);
        }
      } catch {
        if (!cancelled) {
          setError("无法验证登录状态，请稍后重试。");
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    })();

    return () => {
      cancelled = true;
    };
  }, [router]);

  function handleLogout() {
    window.localStorage.removeItem(TOKEN_STORAGE_KEY);
    router.replace("/login");
  }

  if (loading) {
    return (
      <div className="flex min-h-dvh items-center justify-center bg-zinc-50 text-sm text-zinc-600 dark:bg-black dark:text-zinc-400">
        正在验证登录状态…
      </div>
    );
  }

  return (
    <div className="min-h-dvh bg-zinc-50 px-6 py-10 text-zinc-950 dark:bg-black dark:text-zinc-50">
      <div className="mx-auto flex w-full max-w-3xl flex-col gap-6">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-semibold tracking-tight">聊天</h1>
            <p className="mt-2 text-sm leading-6 text-zinc-600 dark:text-zinc-400">
              你已登录。后续会在这里接入会话列表与流式对话。
            </p>
          </div>
          <div className="flex flex-wrap gap-2">
            <Link
              href="/login"
              className="rounded-xl border border-zinc-200 bg-white px-4 py-2 text-sm hover:bg-zinc-100 dark:border-zinc-800 dark:bg-zinc-950 dark:hover:bg-zinc-900"
            >
              登录页
            </Link>
            <button
              type="button"
              onClick={handleLogout}
              className="rounded-xl bg-zinc-950 px-4 py-2 text-sm font-medium text-white hover:bg-zinc-800 dark:bg-zinc-100 dark:text-zinc-950 dark:hover:bg-zinc-300"
            >
              退出登录
            </button>
          </div>
        </div>

        {error ? (
          <div className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700 dark:border-red-900/50 dark:bg-red-950/30 dark:text-red-300">
            {error}
          </div>
        ) : null}

        <section className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-950">
          <h2 className="text-sm font-medium text-zinc-700 dark:text-zinc-300">
            当前用户
          </h2>
          <pre className="mt-3 overflow-x-auto rounded-xl border border-zinc-200 bg-zinc-50 p-4 text-xs leading-6 text-zinc-700 dark:border-zinc-800 dark:bg-zinc-900 dark:text-zinc-300">
            {user ? JSON.stringify(user, null, 2) : "暂无"}
          </pre>
        </section>
      </div>
    </div>
  );
}
