import type { HealthResponse, PulseLatestResponse, StatusResponse } from "./types";

export const API_BASE =
  process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";

async function fetchJson<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    cache: "no-store",
  });
  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || `Request failed: ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export function getHealth() {
  return fetchJson<HealthResponse>("/api/health");
}

export function getStatus() {
  return fetchJson<StatusResponse>("/api/status");
}

export function getLatestPulse() {
  return fetchJson<PulseLatestResponse>("/api/pulse/latest");
}
