export const runtime = "nodejs";

export async function POST(req: Request) {
  const backend = process.env.BACKEND_URL ?? "http://127.0.0.1:8000";
  const body = await req.text();

  const response = await fetch(`${backend}/v1/auth/login`, {
    method: "POST",
    headers: {
      "Content-Type": req.headers.get("Content-Type") ?? "application/json",
      Accept: "application/json",
    },
    body,
    cache: "no-store",
  });

  const text = await response.text();

  return new Response(text, {
    status: response.status,
    headers: {
      "Content-Type": response.headers.get("Content-Type") ?? "application/json",
    },
  });
}
