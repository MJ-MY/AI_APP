export const runtime = "nodejs";

export async function POST(req: Request) {
  const backend = process.env.BACKEND_URL ?? "http://127.0.0.1:8000";
  const body = await req.text();

  const r = await fetch(`${backend}/v1/chat/stream`, {
    method: "POST",
    headers: {
      "Content-Type": req.headers.get("Content-Type") ?? "application/json",
      Accept: "text/event-stream",
    },
    body,
    cache: "no-store",
  });

  return new Response(r.body, {
    status: r.status,
    headers: {
      "Content-Type": "text/event-stream; charset=utf-8",
      "Cache-Control": "no-cache, no-transform",
      Connection: "keep-alive",
    },
  });
}

