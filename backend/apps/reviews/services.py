from __future__ import annotations

from uuid import uuid4

from services.mongodb import mongo_service
from services.notifications import send_review_email


def _next_review_id() -> str:
    return f"rev_{uuid4().hex[:12]}"


def send_review_notification(document_id: str, assigned_team: str):
    review_record = mongo_service.find_one("reviews", {"document_id": document_id}) or {}
    reviewer_email = review_record.get("reviewer_email", f"{assigned_team}@agentdoc.local")
    review_id = review_record.get("review_id") or str(review_record.get("_id", document_id))
    send_review_email(reviewer_email, document_id, review_id)
    mongo_service.append_audit_log(
        document_id,
        "review.notification_sent",
        {"review_id": review_id, "assigned_team": assigned_team, "reviewer_email": reviewer_email},
    )
    return {"document_id": document_id, "review_id": review_id, "reviewer_email": reviewer_email}


def trigger_review_workflow(
    *,
    document_id: str,
    assigned_team: str = "operations",
    reviewer_email: str | None = None,
    instructions: str | None = None,
    due_in_minutes: int = 30,
) -> dict:
    review_record = {
        "review_id": _next_review_id(),
        "document_id": document_id,
        "review_required": True,
        "assigned_team": assigned_team,
        "reviewer_email": reviewer_email or f"{assigned_team}@agentdoc.local",
        "instructions": instructions or "Review extracted fields and verify source evidence.",
        "next_action": "await_human",
        "due_in_minutes": due_in_minutes,
        "review_status": "pending",
        "reviewer_feedback": "",
    }

    existing = mongo_service.find_one("reviews", {"document_id": document_id})
    if existing and existing.get("review_id"):
        review_record["review_id"] = existing["review_id"]

    mongo_service.upsert_one("reviews", {"document_id": document_id}, review_record)
    mongo_service.update_one("documents", {"document_id": document_id}, {"status": "pending_review"})
    mongo_service.append_audit_log(document_id, "review.triggered", review_record)
    notification = send_review_notification(document_id, assigned_team)
    return {"review": review_record, "notification": notification}
