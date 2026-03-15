import { DocumentTable } from "../components/DocumentTable";
import { StatCard } from "../components/StatCard";

export function DashboardPage({ dashboard, loading, onSelectDocument }) {
  const breakdown = dashboard?.status_breakdown || {};

  return (
    <div className="grid gap-4">
      <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-card">
        <p className="text-xs uppercase tracking-[0.2em] text-slate-500">Autonomous Workflow</p>
        <h2 className="mt-1 font-serif text-2xl">Operational intelligence for high-volume document decisions.</h2>
        <p className="mt-2 text-slate-600">
          CrewAI agents classify, extract, validate, route, and escalate documents while Django keeps a full audit trail.
        </p>
      </section>

      <section className="grid grid-cols-1 gap-3 md:grid-cols-2 xl:grid-cols-4">
        <StatCard label="Documents" value={dashboard?.documents_total ?? 0} />
        <StatCard label="Open Reviews" value={dashboard?.reviews_open ?? 0} tone="accent" />
        <StatCard label="Completed" value={breakdown.completed ?? 0} tone="success" />
        <StatCard label="Pending" value={breakdown.pending_review ?? 0} tone="warning" />
      </section>

      {loading ? <div className="text-sm text-slate-500">Refreshing dashboard...</div> : null}

      <DocumentTable documents={dashboard?.recent_documents || []} onSelect={onSelectDocument} />
    </div>
  );
}
