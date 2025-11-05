// src/lib/api.ts
const base = (import.meta.env.VITE_API_BASE || "").replace(/\/$/, "");

export async function chat(message: string) {
  const res = await fetch(`${base}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message }),
  });
  return res.json();
}

export async function predict(form: FormData) {
  const res = await fetch(`${base}/predict`, {
    method: "POST",
    body: form,
  });
  return res.json();
}
