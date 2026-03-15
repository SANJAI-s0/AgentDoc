export function HelpPage() {
  return (
    <section className="space-y-6">
      <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <p className="text-xs uppercase tracking-[0.18em] text-slate-500">Help Center</p>
        <h3 className="mt-2 font-serif text-3xl text-slate-900">Use AgentDoc Efficiently</h3>
        <p className="mt-2 text-sm text-slate-600">
          Quick guidance for upload success, faster reviews, and stronger automation confidence.
        </p>
      </div>

      <div className="grid gap-4 lg:grid-cols-3">
        <article className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
          <h4 className="font-semibold text-slate-900">For Customers</h4>
          <ul className="mt-3 space-y-2 text-sm text-slate-600">
            <li>Upload clear scans and avoid cropped edges.</li>
            <li>Add a document type hint when possible.</li>
            <li>Track status in Dashboard and Documents.</li>
          </ul>
        </article>

        <article className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
          <h4 className="font-semibold text-slate-900">For Reviewers</h4>
          <ul className="mt-3 space-y-2 text-sm text-slate-600">
            <li>Validate extracted fields against source preview.</li>
            <li>Use short, explicit correction comments.</li>
            <li>Approve/reject quickly to reduce SLA delays.</li>
          </ul>
        </article>

        <article className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
          <h4 className="font-semibold text-slate-900">For Operations</h4>
          <ul className="mt-3 space-y-2 text-sm text-slate-600">
            <li>Use semantic search for issue clusters.</li>
            <li>Monitor high-risk routes and exception queues.</li>
            <li>Review audit logs for compliance checks.</li>
          </ul>
        </article>
      </div>

      <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <h4 className="font-semibold text-slate-900">Pro Tips</h4>
        <div className="mt-3 grid gap-3 text-sm text-slate-600 md:grid-cols-2">
          <div className="rounded-xl border border-slate-200 bg-slate-50 p-3">
            Keep MinIO/S3 CORS aligned with frontend origin for presigned uploads.
          </div>
          <div className="rounded-xl border border-slate-200 bg-slate-50 p-3">
            Run the local preflight checker before demos to avoid setup surprises.
          </div>
          <div className="rounded-xl border border-slate-200 bg-slate-50 p-3">
            For low-confidence docs, add a stronger type hint and reprocess.
          </div>
          <div className="rounded-xl border border-slate-200 bg-slate-50 p-3">
            Use search terms like "invoice total" or "kyc government id" for better retrieval.
          </div>
        </div>
      </div>
    </section>
  );
}
