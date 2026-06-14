import type { PulseLatestResponse } from "@/lib/types";
import { formatDate, formatNumber, formatStore } from "@/lib/format";

type PulseViewProps = {
  data: PulseLatestResponse;
};

export function PulseView({ data }: PulseViewProps) {
  const { pulse, validation } = data;

  return (
    <div className="space-y-8">
      <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <h2 className="text-2xl font-semibold text-slate-900">
              {pulse.product} — Weekly Pulse
            </h2>
            <p className="mt-2 text-sm text-slate-600">
              Week ending {formatDate(pulse.week_ending)} ·{" "}
              {pulse.review_window_weeks}-week window (
              {formatDate(pulse.window_start)} – {formatDate(pulse.window_end)})
            </p>
            <p className="mt-1 text-sm text-slate-600">
              {formatNumber(pulse.sample_size)} reviews sampled from{" "}
              {formatNumber(pulse.total_reviews)} total
            </p>
          </div>
          <span
            className={`rounded-full px-3 py-1 text-xs font-semibold ${
              validation.passed
                ? "bg-emerald-100 text-emerald-800"
                : "bg-red-100 text-red-800"
            }`}
          >
            {validation.passed ? "Validation passed" : "Validation failed"}
          </span>
        </div>
      </section>

      <section>
        <h3 className="mb-4 text-lg font-semibold text-slate-900">Top themes</h3>
        <div className="grid gap-4 md:grid-cols-3">
          {pulse.top_themes.map((theme) => (
            <article
              key={theme.theme_id}
              className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm"
            >
              <p className="text-xs font-semibold uppercase text-emerald-700">
                #{theme.rank}
              </p>
              <h4 className="mt-1 font-semibold text-slate-900">{theme.label}</h4>
              <p className="mt-2 text-sm text-slate-600">
                {formatNumber(theme.review_count)} reviews · {theme.avg_rating.toFixed(1)}★
              </p>
              <p className="mt-3 text-sm leading-relaxed text-slate-700">
                {theme.summary}
              </p>
            </article>
          ))}
        </div>
      </section>

      <section>
        <h3 className="mb-4 text-lg font-semibold text-slate-900">User quotes</h3>
        <div className="space-y-3">
          {pulse.quotes.map((quote, index) => (
            <blockquote
              key={`${quote.theme_id}-${index}`}
              className="rounded-xl border-l-4 border-emerald-500 bg-white p-5 shadow-sm"
            >
              <p className="text-xs font-medium text-slate-500">
                {quote.rating}★ · {formatStore(quote.store)}
              </p>
              <p className="mt-2 text-sm leading-relaxed text-slate-800">
                &ldquo;{quote.text}&rdquo;
              </p>
            </blockquote>
          ))}
        </div>
      </section>

      <section>
        <h3 className="mb-4 text-lg font-semibold text-slate-900">
          Recommended actions
        </h3>
        <ol className="space-y-3">
          {pulse.action_ideas.map((action, index) => (
            <li
              key={`${action.theme_id}-${index}`}
              className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm"
            >
              <p className="font-medium text-slate-900">
                {index + 1}. {action.action}
              </p>
              <p className="mt-1 text-sm text-slate-600">{action.rationale}</p>
            </li>
          ))}
        </ol>
      </section>
    </div>
  );
}
