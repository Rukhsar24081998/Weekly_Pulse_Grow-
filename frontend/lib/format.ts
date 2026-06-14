export function formatStore(store: string): string {
  const labels: Record<string, string> = {
    play_store: "Play Store",
    app_store: "App Store",
  };
  return labels[store] ?? store.replace(/_/g, " ");
}

export function formatDate(iso: string): string {
  const date = new Date(`${iso}T00:00:00`);
  if (Number.isNaN(date.getTime())) return iso;
  return date.toLocaleDateString("en-IN", {
    day: "numeric",
    month: "short",
    year: "numeric",
  });
}

export function formatNumber(value: number | undefined): string {
  if (value === undefined) return "—";
  return value.toLocaleString("en-IN");
}
