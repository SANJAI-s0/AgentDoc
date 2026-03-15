export function DocumentTable({ documents = [], onSelect }) {
  const badgeClass = (status) => {
    const value = (status || "").toLowerCase();
    if (value.includes("pending")) return "bg-amber-100 text-amber-800";
    if (value.includes("reject")) return "bg-rose-100 text-rose-800";
    if (value.includes("complete") || value.includes("approved")) return "bg-emerald-100 text-emerald-800";
    if (value.includes("process")) return "bg-blue-100 text-blue-800";
    return "bg-slate-100 text-slate-700";
  };

  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-4 shadow-card">
      <div className="mb-3 flex items-center justify-between">
        <h3 className="font-serif text-xl">Documents</h3>
        <span className="text-sm text-slate-500">{documents.length} visible</span>
      </div>

      <div className="overflow-x-auto">
        <table className="min-w-full text-left text-sm">
          <thead>
            <tr className="text-slate-500">
              <th className="px-2 py-3">ID</th>
              <th className="px-2 py-3">Title</th>
              <th className="px-2 py-3">Type</th>
              <th className="px-2 py-3">Status</th>
              <th className="px-2 py-3">Channel</th>
            </tr>
          </thead>
          <tbody>
            {documents.map((document) => (
              <tr
                key={document.document_id}
                className="cursor-pointer border-t border-slate-100 hover:bg-slate-50"
                onClick={() => onSelect?.(document)}
              >
                <td className="px-2 py-3 font-mono text-xs">{document.document_id}</td>
                <td className="px-2 py-3">{document.title || document.file_name}</td>
                <td className="px-2 py-3">{document.document_type || document.document_type_hint || "pending"}</td>
                <td className="px-2 py-3">
                  <span className={`rounded-full px-2 py-1 text-xs font-medium ${badgeClass(document.status)}`}>
                    {document.status || "unknown"}
                  </span>
                </td>
                <td className="px-2 py-3">{document.source_channel || "web"}</td>
              </tr>
            ))}
            {!documents.length ? (
              <tr>
                <td colSpan={5} className="px-2 py-8 text-center text-slate-500">
                  No documents found for this view.
                </td>
              </tr>
            ) : null}
          </tbody>
        </table>
      </div>
    </div>
  );
}
