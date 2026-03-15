import { NavLink } from "react-router-dom";

export function AppShell({ currentUser, onLogout, children }) {
  const isReviewer = ["reviewer", "admin"].includes(currentUser?.role);

  const linkClass = ({ isActive }) =>
    [
      "flex items-center gap-2 rounded-xl border px-3 py-2 text-sm capitalize transition",
      isActive
        ? "border-white/30 bg-white/15 text-white"
        : "border-transparent text-blue-100 hover:border-white/20 hover:bg-white/10",
    ].join(" ");

  return (
    <div className="min-h-screen bg-gradient-to-b from-sand to-slate-100 text-ink">
      <div className="grid min-h-screen grid-cols-1 lg:grid-cols-[320px_1fr]">
        <aside className="border-b border-white/20 bg-gradient-to-b from-slate-900 to-slate-700 p-6 text-white lg:border-b-0 lg:border-r">
          <div className="space-y-3">
            <p className="text-xs uppercase tracking-[0.2em] text-blue-200">AgentDoc</p>
            <h1 className="font-serif text-2xl">Intelligent Document Operations</h1>
            <p className="text-sm text-blue-100">
              Autonomous workflow automation for KYC, invoices, receipts, claims, shipping documents, and contracts.
            </p>
          </div>

          <div className="mt-6 rounded-2xl border border-white/20 bg-white/10 p-4">
            <p className="text-xs uppercase tracking-[0.15em] text-blue-200">Active Session</p>
            <h3 className="mt-1 text-lg">{currentUser?.display_name}</h3>
            <p className="text-sm text-blue-100">
              {currentUser?.role} · {currentUser?.user_id}
            </p>
            <button
              className="mt-3 w-full rounded-xl border border-white/30 bg-white/15 px-3 py-2 text-sm hover:bg-white/25"
              onClick={onLogout}
            >
              Logout
            </button>
          </div>

          <nav className="mt-6 grid gap-2">
            <NavLink to="/dashboard" className={linkClass}>
              <span className="h-2 w-2 rounded-full bg-blue-300" /> dashboard
            </NavLink>
            <NavLink to="/documents" className={linkClass}>
              <span className="h-2 w-2 rounded-full bg-blue-300" /> documents
            </NavLink>
            <NavLink to="/search" className={linkClass}>
              <span className="h-2 w-2 rounded-full bg-blue-300" /> search
            </NavLink>
            <NavLink to="/help" className={linkClass}>
              <span className="h-2 w-2 rounded-full bg-blue-300" /> help
            </NavLink>
            {isReviewer ? (
              <NavLink to="/reviews" className={linkClass}>
                <span className="h-2 w-2 rounded-full bg-blue-300" /> reviews
              </NavLink>
            ) : null}
          </nav>
        </aside>

        <main className="p-4 md:p-6 lg:p-8">{children}</main>
      </div>
    </div>
  );
}
