import { useEffect, useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Document, Page, pdfjs } from "react-pdf";
import "react-pdf/dist/Page/TextLayer.css";
import "react-pdf/dist/Page/AnnotationLayer.css";
import { api } from "../api/client";
import { ReviewQueue } from "../components/ReviewQueue";

pdfjs.GlobalWorkerOptions.workerSrc = `https://unpkg.com/pdfjs-dist@${pdfjs.version}/build/pdf.worker.min.js`;

export function ReviewsPage({ reviews, onDecision, decisionInFlight }) {
  const [selectedReview, setSelectedReview] = useState(null);
  const [jsonText, setJsonText] = useState("{}");
  const [feedback, setFeedback] = useState("Reviewed in console.");

  useEffect(() => {
    if (!selectedReview && reviews?.length) {
      setSelectedReview(reviews[0]);
    }
  }, [reviews, selectedReview]);

  const selectedDocumentId = selectedReview?.document_id;

  const detailQuery = useQuery({
    queryKey: ["review-document", selectedDocumentId],
    queryFn: () => api.getDocumentDetail(selectedDocumentId),
    enabled: Boolean(selectedDocumentId),
    refetchInterval: 10_000,
  });

  const extractionFields = useMemo(() => {
    return detailQuery.data?.extraction?.structured_fields || {};
  }, [detailQuery.data]);

  useEffect(() => {
    setJsonText(JSON.stringify(extractionFields, null, 2));
  }, [extractionFields, selectedDocumentId]);

  const documentMeta = detailQuery.data?.document || {};
  const fileUrl = documentMeta?.file_urls?.[0] || documentMeta?.storage_path || "";
  const isPdf = (documentMeta?.mime_type || "").toLowerCase().includes("pdf") || fileUrl.toLowerCase().endsWith(".pdf");

  const handleDecision = async (decision) => {
    if (!selectedReview) return;

    let correctedFields = {};
    try {
      correctedFields = JSON.parse(jsonText || "{}");
    } catch {
      correctedFields = extractionFields || {};
    }

    await onDecision({
      reviewId: selectedReview.review_id,
      documentId: selectedReview.document_id,
      decision,
      reviewer_feedback: feedback,
      corrected_fields: correctedFields,
    });
  };

  return (
    <div className="grid gap-4 xl:grid-cols-[340px_1fr]">
      <ReviewQueue reviews={reviews} onSelect={setSelectedReview} />

      <section className="rounded-2xl border border-slate-200 bg-white p-4 shadow-card">
        {!selectedReview ? (
          <p className="text-sm text-slate-500">Select a review item to inspect source document and extracted JSON.</p>
        ) : (
          <div className="grid gap-4">
            <header className="flex flex-wrap items-start justify-between gap-2 border-b border-slate-200 pb-3">
              <div>
                <p className="text-xs uppercase tracking-wide text-slate-500">Review Workspace</p>
                <h3 className="font-serif text-2xl">{selectedReview.document_id}</h3>
                <p className="text-sm text-slate-600">{selectedReview.instructions || "Validate extracted fields against source evidence."}</p>
              </div>
              <span className="rounded-full bg-amber-100 px-3 py-1 text-xs font-medium text-amber-800">
                {selectedReview.next_action || "await_human"}
              </span>
            </header>

            <div className="grid gap-4 xl:grid-cols-2">
              <div className="rounded-xl border border-slate-200 bg-slate-50 p-3">
                <h4 className="mb-2 font-medium">Source Document</h4>
                {detailQuery.isLoading ? <p className="text-sm text-slate-500">Loading document...</p> : null}
                {!detailQuery.isLoading && fileUrl ? (
                  <div className="max-h-[620px] overflow-auto rounded border border-slate-200 bg-white p-2">
                    {isPdf ? (
                      <Document file={fileUrl} loading="Loading PDF...">
                        <Page pageNumber={1} width={520} />
                      </Document>
                    ) : (
                      <img src={fileUrl} alt="Document preview" className="h-auto max-w-full rounded" />
                    )}
                  </div>
                ) : null}
                {!detailQuery.isLoading && !fileUrl ? <p className="text-sm text-slate-500">No preview URL available.</p> : null}
              </div>

              <div className="rounded-xl border border-slate-200 bg-slate-50 p-3">
                <h4 className="mb-2 font-medium">Extracted JSON (Editable)</h4>
                <textarea
                  className="min-h-[420px] w-full rounded border border-slate-300 bg-white p-3 font-mono text-xs"
                  value={jsonText}
                  onChange={(event) => setJsonText(event.target.value)}
                />

                <label className="mt-3 grid gap-1">
                  <span className="text-sm text-slate-600">Reviewer feedback</span>
                  <textarea
                    className="min-h-[90px] rounded border border-slate-300 bg-white p-3 text-sm"
                    value={feedback}
                    onChange={(event) => setFeedback(event.target.value)}
                  />
                </label>

                <div className="mt-3 flex flex-wrap gap-2">
                  <button
                    className="rounded-xl bg-emerald-600 px-3 py-2 text-sm text-white hover:bg-emerald-700"
                    onClick={() => handleDecision("approve")}
                    disabled={decisionInFlight}
                  >
                    Approve
                  </button>
                  <button
                    className="rounded-xl bg-amber-600 px-3 py-2 text-sm text-white hover:bg-amber-700"
                    onClick={() => handleDecision("request_changes")}
                    disabled={decisionInFlight}
                  >
                    Request Changes
                  </button>
                  <button
                    className="rounded-xl bg-rose-600 px-3 py-2 text-sm text-white hover:bg-rose-700"
                    onClick={() => handleDecision("reject")}
                    disabled={decisionInFlight}
                  >
                    Reject
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
      </section>
    </div>
  );
}
