import pulseLatest from "../public/data/pulse-latest.json";
import statusSnapshot from "../public/data/status.json";
import type { HealthResponse, PulseLatestResponse, StatusResponse } from "./types";

const REMOTE_API =
  process.env.VERCEL || process.env.NEXT_PUBLIC_USE_STATIC === "true"
    ? ""
    : (process.env.NEXT_PUBLIC_API_URL ?? "").replace(/\/$/, "");

async function fetchJson<T>(url: string): Promise<T> {
  const response = await fetch(url, { cache: "no-store" });
  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || `Request failed: ${response.status}`);
  }
  return response.json() as Promise<T>;
}

function remoteUrl(path: string): string {
  return `${REMOTE_API}${path}`;
}

export async function getHealth() {
  if (REMOTE_API) {
    return fetchJson<HealthResponse>(remoteUrl("/api/health"));
  }
  return {
    status: "ok",
    service: "weekly-app-review-pulse-static",
    product: statusSnapshot.product,
    artifacts: statusSnapshot.artifacts,
  } satisfies HealthResponse;
}

export async function getStatus() {
  if (REMOTE_API) {
    return fetchJson<StatusResponse>(remoteUrl("/api/status"));
  }
  return statusSnapshot as StatusResponse;
}

export async function getLatestPulse() {
  if (REMOTE_API) {
    return fetchJson<PulseLatestResponse>(remoteUrl("/api/pulse/latest"));
  }
  return pulseLatest as PulseLatestResponse;
}
