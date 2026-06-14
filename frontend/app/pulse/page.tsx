import { ErrorPanel } from "@/components/ErrorPanel";
import { PulseView } from "@/components/PulseView";
import { getLatestPulse } from "@/lib/api";

export default async function PulsePage() {
  try {
    const data = await getLatestPulse();
    return (
      <div className="space-y-6">
        <div>
          <h2 className="text-2xl font-semibold text-slate-900">Weekly pulse</h2>
          <p className="mt-1 text-sm text-slate-600">
            Rendered from <code className="rounded bg-slate-200 px-1">/api/pulse/latest</code>
          </p>
        </div>
        <PulseView data={data} />
      </div>
    );
  } catch {
    return (
      <ErrorPanel
        title="Pulse not available"
        message="Ensure the API is running and you have generated a pulse with python -m src.pulse.run."
      />
    );
  }
}
