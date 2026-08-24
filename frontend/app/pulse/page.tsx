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
            Latest generated weekly note.
          </p>
        </div>
        <PulseView data={data} />
      </div>
    );
  } catch {
    return (
      <ErrorPanel
        title="Pulse not available"
        message="Trigger Actions → Weekly Pulse, then refresh this page."
      />
    );
  }
}
