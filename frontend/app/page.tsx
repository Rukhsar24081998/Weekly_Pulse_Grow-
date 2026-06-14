import Link from "next/link";

import { ErrorPanel } from "@/components/ErrorPanel";
import { StatCard } from "@/components/StatCard";
import { getLatestPulse, getStatus } from "@/lib/api";
import { formatDate, formatNumber } from "@/lib/format";

export default async function DashboardPage() {
  let status;
  let pulseData;

  try {
    status = await getStatus();
  } catch {
    status = null;
  }

  try {
    pulseData = await getLatestPulse();
  } catch {
    pulseData = null;
  }

  if (!status && !pulseData) {
    return (
      <ErrorPanel
        title="API not reachable"
        message="Start the Python API on port 8000, then run the pipeline to generate pulse artifacts."
      />
    );
  }

  const reviews = status?.reviews;
  const summary = status?.pulse_summary;
  const docUrl = status?.doc?.google_doc_url ?? status?.last_publish?.google_doc_url;

  return (
    <div className="space-y-8">
      <section>
        <h2 className="text-2xl font-semibold text-slate-900">Dashboard</h2>
        <p className="mt-1 text-sm text-slate-600">
          Latest pipeline snapshot from your local API.
        </p>
      </section>

      <section className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard
          label="Total reviews"
          value={formatNumber(reviews?.total)}
          hint="In current ingest window"
        />
        <StatCard
          label="Play Store"
          value={formatNumber(reviews?.play_store)}
        />
        <StatCard
          label="App Store"
          value={formatNumber(reviews?.app_store)}
        />
        <StatCard
          label="Pulse words"
          value={summary?.word_count?.toString() ?? "—"}
          hint={
            summary?.week_ending
              ? `Week ending ${formatDate(summary.week_ending)}`
              : undefined
          }
        />
      </section>

      {docUrl ? (
        <section className="rounded-xl border border-emerald-200 bg-emerald-50 p-5">
          <p className="text-sm font-medium text-emerald-900">Latest Google Doc</p>
          <a
            href={docUrl}
            target="_blank"
            rel="noreferrer"
            className="mt-2 inline-block text-sm text-emerald-800 underline"
          >
            Open published pulse
          </a>
        </section>
      ) : null}

      {pulseData ? (
        <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div>
              <h3 className="text-lg font-semibold text-slate-900">Latest pulse ready</h3>
              <p className="mt-1 text-sm text-slate-600">
                Week ending {formatDate(pulseData.pulse.week_ending)} ·{" "}
                {pulseData.pulse.word_count} words ·{" "}
                {pulseData.validation.passed ? "validated" : "needs review"}
              </p>
            </div>
            <Link
              href="/pulse"
              className="rounded-lg bg-emerald-700 px-4 py-2 text-sm font-medium text-white hover:bg-emerald-800"
            >
              View pulse
            </Link>
          </div>
        </section>
      ) : (
        <ErrorPanel
          title="No pulse artifact yet"
          message="Run the pipeline to create phases/phase-3/pulse.json, then refresh this page."
        />
      )}
    </div>
  );
}
