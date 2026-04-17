export const runtime = "nodejs";

export async function GET(req: Request) {
  const backend = process.env.BACKEND_URL ?? "http://127.0.0.1:8000";
  const authorization = req.headers.get("Authorization");

  const response = await fetch(`${backend}/v1/auth/me`, {
    method: "GET",
    headers: {
      Accept: "application/json",
      ...(authorization ? { Authorization: authorization } : {}),
    },
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
