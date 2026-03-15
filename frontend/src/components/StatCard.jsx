export function StatCard({ label, value, tone = "default" }) {
  const toneClass = {
    default: "bg-white",
    accent: "bg-blue-50",
    success: "bg-emerald-50",
    warning: "bg-amber-50",
  }[tone] || "bg-white";

  return (
    <div className={`rounded-2xl border border-slate-200 p-4 shadow-card ${toneClass}`}>
      <p className="text-sm text-slate-500">{label}</p>
      <p className="mt-2 text-3xl font-semibold">{value}</p>
    </div>
  );
}
