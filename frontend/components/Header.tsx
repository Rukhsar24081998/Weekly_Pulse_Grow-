import Link from "next/link";

export function Header() {
  return (
    <header className="border-b border-slate-200 bg-white">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
        <div>
          <p className="text-xs font-semibold uppercase tracking-wider text-emerald-700">
            Weekly App Review Pulse
          </p>
          <h1 className="text-lg font-semibold text-slate-900">Groww App</h1>
        </div>
        <nav className="flex gap-4 text-sm font-medium">
          <Link href="/" className="text-slate-600 hover:text-emerald-700">
            Dashboard
          </Link>
          <Link href="/pulse" className="text-slate-600 hover:text-emerald-700">
            Pulse
          </Link>
        </nav>
      </div>
    </header>
  );
}
