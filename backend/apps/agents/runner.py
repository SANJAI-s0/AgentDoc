from __future__ import annotations

import logging

from apps.reviews.services import trigger_review_workflow
from services.mongodb import mongo_service
from services.vector_search import vector_search_service

from .crew import document_crew_factory
from .events import emit_agent_stage_completed
from .workflow import run_document_workflow_sync

logger = logging.getLogger(__name__)


def _model_dump(model) -> dict | None:
    return model.model_dump() if model else None


def _persist_pages(state) -> None:
    if not state.preprocessing:
        return
    for page in state.preprocessing.pages:
        page_payload = page.model_dump() if hasattr(page, "model_dump") else dict(page)
        mongo_service.upsert_one(
            "pages",
            {"document_id": state.document_id, "page_number": page_payload["page_number"]},
            {
                **page_payload,
                "document_id": state.document_id,
                "clean_image_url": page_payload.get("storage_path") or page_payload.get("clean_image_url"),
            },
        )


def _persist_state(state) -> None:
    doc_id = state.document_id

    mongo_service.update_one(
        "documents",
        {"document_id": doc_id},
        {
            "status": state.audit.workflow_status if state.audit else "processing",
            "document_type": state.classification.document_type if state.classification else None,
            "searchable_summary": state.audit.searchable_summary if state.audit else None,
        },
    )

    _persist_pages(state)

    if state.extraction:
        mongo_service.upsert_one("extractions", {"document_id": doc_id}, state.extraction.model_dump())

    if state.validation:
        mongo_service.upsert_one("validation_results", {"document_id": doc_id}, state.validation.model_dump())

    if state.review:
        review_payload = state.review.model_dump()
        existing = mongo_service.find_one("reviews", {"document_id": doc_id}) or {}
        review_payload["review_id"] = (
            review_payload.get("review_id")
            or existing.get("review_id")
            or f"rev_{doc_id.split('_')[-1]}"
        )
        if existing.get("reviewer_email") and not review_payload.get("reviewer_email"):
            review_payload["reviewer_email"] = existing["reviewer_email"]
        if review_payload.get("review_required") and not review_payload.get("reviewer_email"):
            review_payload["reviewer_email"] = "operations@agentdoc.local"
        mongo_service.upsert_one("reviews", {"document_id": doc_id}, review_payload)

    if state.audit:
        mongo_service.insert_one("audit_logs", state.audit.model_dump())
        vector_search_service.update_document_embedding(doc_id, state.audit.searchable_summary)


def _emit_stage_events(state) -> None:
    stages = {
        "ingestion": state.ingestion,
        "preprocessing": state.preprocessing,
        "classification": state.classification,
        "extraction": state.extraction,
        "validation": state.validation,
        "routing": state.routing,
        "exception": state.exception,
        "review": state.review,
        "audit": state.audit,
    }
    for stage, model in stages.items():
        payload = _model_dump(model)
        if payload:
            emit_agent_stage_completed(state.document_id, stage, payload)


def execute_document_workflow(payload: dict):
    """Run the full 5-agent workflow, persist results, and trigger review if needed."""
    fallback_reason = None
    try:
        state = run_document_workflow_sync(payload)
    except Exception as exc:
        fallback_reason = str(exc)
        logger.warning("Workflow error for %s, using simulation: %s", payload.get("document_id"), exc)
        state = document_crew_factory.simulate(payload)

    _persist_state(state)
    _emit_stage_events(state)

    audit_payload = state.audit.model_dump() if state.audit else {}
    mongo_service.append_audit_log(payload["document_id"], "workflow.completed", audit_payload)

    if fallback_reason:
        mongo_service.append_audit_log(
            payload["document_id"],
            "workflow.fallback_simulation",
            {"reason": fallback_reason[:400]},
        )

    if state.review and state.review.review_required:
        trigger_review_workflow(
            document_id=payload["document_id"],
            assigned_team=state.review.assigned_team,
            reviewer_email=None,
            instructions=state.review.instructions,
            due_in_minutes=state.review.due_in_minutes,
        )

    return state
