/**
 * lib/api.ts - Centralized API client for backend communication.
 *
 * All fetch calls to the backend go through this module.
 * Handles cookie-based session auth and error parsing.
 */
import { API_BASE } from "../constants";
import type { GenerateResult } from "../types";

// ── Generic fetch helper ─────────────────────────────────────────────────────

async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    credentials: "include",
    headers: { "Content-Type": "application/json", ...options?.headers },
    ...options,
  });
  if (!res.ok) {
    const errText = await res.text();
    let msg = `Server error (${res.status})`;
    try {
      const j = JSON.parse(errText);
      msg = j.error || j.detail || msg;
    } catch { /* keep default msg */ }
    throw new Error(msg);
  }
  return res.json();
}

// ── Actions ──────────────────────────────────────────────────────────────────

export async function generatePost(params: {
  topic: string;
  template_id: number;
  category?: string;
  brand_name?: string;
  cta_text?: string;
}): Promise<GenerateResult> {
  const data = await apiFetch<GenerateResult & { error?: string }>("/api/generate", {
    method: "POST",
    body: JSON.stringify(params),
  });
  if (data.error) throw new Error(data.error);
  return data;
}