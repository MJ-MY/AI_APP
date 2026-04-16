export const runtime = "nodejs";

export async function GET() {
  const backend = process.env.BACKEND_URL ?? "http://127.0.0.1:8000";
  const r = await fetch(`${backend}/health`, {
    method: "GET",
    headers: {
      Accept: "application/json",
    },
    cache: "no-store",
  });

  const text = await r.text();
  return new Response(text, {
    status: r.status,
    headers: {
      "Content-Type": r.headers.get("Content-Type") ?? "application/json",
    },
  });
}

