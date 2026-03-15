import { useMemo, useState } from "react";
import { DocumentTable } from "../components/DocumentTable";

export function SearchPage({ searchResults, onSearch, searching, onSelectDocument }) {
  const [query, setQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");

  const handleSearch = async (event) => {
    event.preventDefault();
    await onSearch(query);
  };

  const filtered = useMemo(() => {
    if (statusFilter === "all") return searchResults;
    return searchResults.filter((item) => (item.status || "").toLowerCase() === statusFilter);
  }, [searchResults, statusFilter]);

  return (
    <div className="grid gap-4">
      <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-card">
        <div className="mb-3 flex flex-wrap items-end gap-3">
          <div className="grow">
            <h3 className="font-serif text-2xl">Semantic Search</h3>
            <p className="text-sm text-slate-500">Find documents by intent, extracted meaning, or keywords.</p>
          </div>

          <label className="grid gap-1 text-sm text-slate-600">
            Status filter
            <select
              className="rounded-xl border border-slate-300 px-3 py-2"
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
            >
              <option value="all">All</option>
              <option value="processing">Processing</option>
              <option value="pending_review">Pending Review</option>
              <option value="completed">Completed</option>
              <option value="rejected">Rejected</option>
            </select>
          </label>
        </div>

        <form className="flex flex-wrap gap-2" onSubmit={handleSearch}>
          <input
            className="min-w-[260px] grow rounded-xl border border-slate-300 px-3 py-2"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search: invoice total, customer name, claim mismatch, etc."
          />
          <button className="rounded-xl bg-ocean px-4 py-2 text-white hover:bg-sky-700" type="submit" disabled={searching}>
            {searching ? "Searching..." : "Search"}
          </button>
        </form>
      </section>

      <DocumentTable documents={filtered} onSelect={onSelectDocument} />
    </div>
  );
}
