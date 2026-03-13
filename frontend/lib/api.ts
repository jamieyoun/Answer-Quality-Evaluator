const API_BASE =
  process.env.NEXT_PUBLIC_BACKEND_BASE_URL ?? "http://127.0.0.1:8000";

export async function fetchCompare(params: {
  q: string;
  top_k: number;
  include_c: boolean;
  alpha: number;
}) {
  const url = new URL(`${API_BASE}/run/compare`);
  url.searchParams.set("q", params.q);
  url.searchParams.set("top_k", String(params.top_k));
  url.searchParams.set("include_c", String(params.include_c));
  url.searchParams.set("alpha", String(params.alpha));

  const res = await fetch(url.toString());
  if (!res.ok) {
    throw new Error(`Compare request failed: ${res.status}`);
  }
  return res.json();
}

export async function fetchEvalResults(runId: string) {
  const url = new URL(`${API_BASE}/eval/results`);
  url.searchParams.set("run_id", runId);
  const res = await fetch(url.toString());
  if (!res.ok) {
    throw new Error(`Eval results failed: ${res.status}`);
  }
  return res.json();
}

