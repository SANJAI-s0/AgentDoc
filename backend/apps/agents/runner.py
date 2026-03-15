from __future__ import annotations

from apps.reviews.services import trigger_review_workflow
from services.mongodb import mongo_service
from services.vector_search import vector_search_service

from .crew import document_crew_factory
from .events import emit_agent_stage_completed
from .workflow import run_document_workflow_sync


def _model_dump(model):
    return model.model_dump() if model else None


def _persist_pages(state):
    if not state.preprocessing:
        return
    for page in state.preprocessing.pages:
        page_payload = page.model_dump() if hasattr(page, "model_dump") else dict(page)
        mongo_service.upsert_one(
            "pages",
            {
                "document_id": state.document_id,
                "page_number": page_payload["page_number"],
            },
            {
                **page_payload,
                "document_id": state.document_id,
                "clean_image_url": page_payload.get("storage_path") or page_payload.get("clean_image_url"),
            },
        )


def _persist_state(state):
    document_id = state.document_id

    mongo_service.update_one(
        "documents",
        {"document_id": document_id},
        {
            "status": state.audit.workflow_status if state.audit else "processing",
            "document_type": state.classification.document_type if state.classification else None,
            "searchable_summary": state.audit.searchable_summary if state.audit else None,
        },
    )

    _persist_pages(state)

    if state.extraction:
        mongo_service.upsert_one("extractions", {"document_id": document_id}, state.extraction.model_dump())

    if state.validation:
        mongo_service.upsert_one("validation_results", {"document_id": document_id}, state.validation.model_dump())

    if state.review:
        review_payload = state.review.model_dump()
        existing_review = mongo_service.find_one("reviews", {"document_id": document_id}) or {}
        review_payload["review_id"] = (
            review_payload.get("review_id")
            or existing_review.get("review_id")
            or f"rev_{document_id.split('_')[-1]}"
        )
        if existing_review.get("reviewer_email") and not review_payload.get("reviewer_email"):
            review_payload["reviewer_email"] = existing_review["reviewer_email"]
        if review_payload.get("review_required") and not review_payload.get("reviewer_email"):
            review_payload["reviewer_email"] = "operations@agentdoc.local"
        mongo_service.upsert_one("reviews", {"document_id": document_id}, review_payload)

    if state.audit:
        mongo_service.insert_one("audit_logs", state.audit.model_dump())
        vector_search_service.update_document_embedding(document_id, state.audit.searchable_summary)


def _emit_stage_events(state):
    stage_map = {
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
    for stage, model in stage_map.items():
        payload = _model_dump(model)
        if payload:
            emit_agent_stage_completed(state.document_id, stage, payload)


def execute_document_workflow(payload: dict):
    fallback_reason = None
    try:
        state = run_document_workflow_sync(payload)
    except Exception as exc:  # pragma: no cover - runtime safety guard
        fallback_reason = str(exc)
        state = document_crew_factory.simulate(payload)

    _persist_state(state)
    _emit_stage_events(state)

    mongo_service.append_audit_log(payload["document_id"], "workflow.completed", state.audit.model_dump() if state.audit else {})

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
