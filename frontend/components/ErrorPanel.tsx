type ErrorPanelProps = {
  title: string;
  message: string;
};

export function ErrorPanel({ title, message }: ErrorPanelProps) {
  return (
    <div className="rounded-xl border border-amber-200 bg-amber-50 p-6 text-amber-950">
      <h2 className="text-lg font-semibold">{title}</h2>
      <p className="mt-2 text-sm leading-relaxed">{message}</p>
      <pre className="mt-4 overflow-x-auto rounded-lg bg-white p-4 text-xs text-slate-700">
        python -m src.ingest.run{"\n"}
        python -m src.themes.run --no-groq{"\n"}
        python -m src.pulse.run{"\n"}
        python -m src.api
      </pre>
    </div>
  );
}
