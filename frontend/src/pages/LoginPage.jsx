import { useState } from "react";

export function LoginPage({ onLogin, notice }) {
  const [formState, setFormState] = useState({
    username: "customer_demo",
    password: "DemoPass123!",
  });
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (event) => {
    event.preventDefault();
    setSubmitting(true);
    setError("");
    try {
      await onLogin(formState);
    } catch (loginError) {
      setError(loginError.message || "Unable to sign in.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="grid min-h-screen place-items-center bg-gradient-to-b from-sand to-slate-100 p-4">
      <section className="grid w-full max-w-xl gap-4 rounded-3xl border border-slate-200 bg-white p-6 shadow-card">
        <p className="text-xs uppercase tracking-[0.2em] text-slate-500">Agentic Document Platform</p>
        <h1 className="font-serif text-3xl">Sign in to continue</h1>
        <p className="text-slate-600">
          Secure access to autonomous workflows for KYC, invoices, receipts, claims, shipping documents, loan applications, and contracts.
        </p>

        <form className="grid gap-3" onSubmit={handleSubmit}>
          <label className="grid gap-1">
            <span className="text-sm text-slate-600">Username</span>
            <input
              className="rounded-xl border border-slate-300 px-3 py-2"
              value={formState.username}
              onChange={(event) => setFormState({ ...formState, username: event.target.value })}
            />
          </label>

          <label className="grid gap-1">
            <span className="text-sm text-slate-600">Password</span>
            <input
              className="rounded-xl border border-slate-300 px-3 py-2"
              type="password"
              value={formState.password}
              onChange={(event) => setFormState({ ...formState, password: event.target.value })}
            />
          </label>

          <button className="rounded-xl bg-ocean px-4 py-2 text-white hover:bg-sky-700" type="submit" disabled={submitting}>
            {submitting ? "Signing in..." : "Login"}
          </button>
        </form>

        {error ? <p className="text-sm text-rose-700">{error}</p> : null}

        <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4 text-sm text-slate-700">
          <p><strong>Customer:</strong> <code>customer_demo</code> / <code>DemoPass123!</code></p>
          <p><strong>Reviewer:</strong> <code>reviewer_demo</code> / <code>DemoPass123!</code></p>
          <p className="mt-2 text-slate-500">{notice}</p>
        </div>
      </section>
    </div>
  );
}
