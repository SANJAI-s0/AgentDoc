export function ReviewQueue({ reviews = [], onSelect }) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-4 shadow-card">
      <div className="mb-3 flex items-center justify-between">
        <h3 className="font-serif text-xl">Human Review Queue</h3>
        <span className="text-sm text-slate-500">{reviews.length} items</span>
      </div>
      <div className="grid gap-3">
        {reviews.map((review) => (
          <button
            key={review.review_id || review.document_id}
            className="rounded-xl border border-slate-200 bg-slate-50 p-4 text-left hover:border-blue-300 hover:bg-blue-50"
            onClick={() => onSelect?.(review)}
          >
            <p className="text-xs uppercase tracking-wide text-slate-500">{review.assigned_team || "operations"}</p>
            <p className="mt-1 font-mono text-sm text-slate-700">{review.document_id}</p>
            <p className="mt-2 text-sm text-slate-700">{review.instructions || "Review instructions will appear here."}</p>
            <p className="mt-2 text-xs text-slate-500">Due: {review.due_in_minutes ? `${review.due_in_minutes} mins` : "ASAP"}</p>
          </button>
        ))}
        {!reviews.length ? <div className="py-6 text-center text-sm text-slate-500">No documents currently require human review.</div> : null}
      </div>
    </div>
  );
}
