import { useState } from "react";
import { DocumentTable } from "../components/DocumentTable";

const initialForm = {
  title: "",
  source_channel: "web",
  document_type_hint: "invoice",
  force_review: false,
};

export function DocumentsPage({ currentUser, documents, onUpload, uploadProgress, uploading, onSelectDocument }) {
  const [formState, setFormState] = useState(initialForm);
  const [file, setFile] = useState(null);
  const [dragActive, setDragActive] = useState(false);

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!file) return;

    await onUpload({ file, formState });
    setFormState((prev) => ({ ...prev, title: "" }));
    setFile(null);
  };

  const onDrop = (event) => {
    event.preventDefault();
    setDragActive(false);
    const droppedFile = event.dataTransfer.files?.[0];
    if (droppedFile) setFile(droppedFile);
  };

  return (
    <div className="grid gap-4">
      <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-card">
        <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
          <div>
            <h3 className="font-serif text-2xl">Submit Document</h3>
            <p className="text-sm text-slate-500">Signed in as {currentUser?.display_name}</p>
          </div>
          <span className="rounded-full bg-blue-50 px-3 py-1 text-xs font-medium text-blue-700">B2C intake portal</span>
        </div>

        <form className="grid gap-3" onSubmit={handleSubmit}>
          <div className="grid gap-3 md:grid-cols-2">
            <label className="grid gap-1">
              <span className="text-sm text-slate-600">Title</span>
              <input
                className="rounded-xl border border-slate-300 px-3 py-2"
                value={formState.title}
                onChange={(e) => setFormState({ ...formState, title: e.target.value })}
                placeholder="March utility bill"
              />
            </label>

            <label className="grid gap-1">
              <span className="text-sm text-slate-600">Source</span>
              <select
                className="rounded-xl border border-slate-300 px-3 py-2"
                value={formState.source_channel}
                onChange={(e) => setFormState({ ...formState, source_channel: e.target.value })}
              >
                <option value="web">Web</option>
                <option value="mobile">Mobile</option>
                <option value="email">Email</option>
                <option value="api">API</option>
              </select>
            </label>

            <label className="grid gap-1 md:col-span-2">
              <span className="text-sm text-slate-600">Document Type Hint</span>
              <select
                className="rounded-xl border border-slate-300 px-3 py-2"
                value={formState.document_type_hint}
                onChange={(e) => setFormState({ ...formState, document_type_hint: e.target.value })}
              >
                <option value="invoice">Invoice</option>
                <option value="receipt">Receipt</option>
                <option value="kyc_form">KYC form</option>
                <option value="loan_application">Loan application</option>
                <option value="insurance_claim">Insurance claim</option>
                <option value="shipping_document">Shipping document</option>
                <option value="contract">Contract</option>
                <option value="handwritten_form">Handwritten form</option>
              </select>
            </label>
          </div>

          <label className="inline-flex items-center gap-2 text-sm text-slate-600">
            <input
              type="checkbox"
              checked={formState.force_review}
              onChange={(e) => setFormState({ ...formState, force_review: e.target.checked })}
            />
            Force human review for this submission
          </label>

          <div
            className={`rounded-2xl border-2 border-dashed p-6 text-center transition ${
              dragActive ? "border-blue-400 bg-blue-50" : "border-slate-300 bg-slate-50"
            }`}
            onDragOver={(e) => {
              e.preventDefault();
              setDragActive(true);
            }}
            onDragLeave={() => setDragActive(false)}
            onDrop={onDrop}
          >
            <p className="text-sm text-slate-600">Drag and drop a document here, or choose a file</p>
            <input
              className="mt-3 block w-full text-sm"
              type="file"
              onChange={(e) => setFile(e.target.files?.[0] || null)}
            />
            {file ? <p className="mt-2 text-sm text-slate-700">Selected: {file.name}</p> : null}
          </div>

          {uploading ? (
            <div className="space-y-1">
              <div className="h-2 rounded-full bg-slate-200">
                <div className="h-2 rounded-full bg-blue-600" style={{ width: `${uploadProgress}%` }} />
              </div>
              <p className="text-xs text-slate-500">Upload progress: {uploadProgress}%</p>
            </div>
          ) : null}

          <button
            type="submit"
            disabled={!file || uploading}
            className="rounded-xl bg-ocean px-4 py-2 text-white hover:bg-sky-700 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {uploading ? "Uploading..." : "Process Document"}
          </button>
        </form>
      </section>

      <DocumentTable documents={documents} onSelect={onSelectDocument} />
    </div>
  );
}
