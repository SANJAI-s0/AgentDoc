from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class PageDescriptor(BaseModel):
    page_number: int
    mime_type: str
    storage_path: str | None = None
    ocr_text: str | None = None
    confidence: float | None = None


class IngestionOutput(BaseModel):
    document_id: str
    user_id: str
    source_channel: Literal["web", "mobile", "email", "api"]
    storage_path: str
    file_name: str
    mime_type: str
    page_count: int
    checksum: str
    file_urls: list[str] = Field(default_factory=list)
    status: Literal["accepted", "rejected"] = "accepted"
    priority: Literal["low", "normal", "high"] = "normal"
    next_action: Literal["preprocess", "reject"]
    reasons: list[str] = Field(default_factory=list)


class PreprocessingOutput(BaseModel):
    document_id: str
    image_quality_score: float
    detected_languages: list[str]
    rotation_applied: int = 0
    pages: list[PageDescriptor]
    next_action: Literal["classify", "manual_review"]
    reasons: list[str] = Field(default_factory=list)


class ClassificationOutput(BaseModel):
    document_id: str
    document_type: Literal[
        "kyc_form",
        "invoice",
        "receipt",
        "insurance_claim",
        "shipping_document",
        "loan_application",
        "contract",
        "handwritten_form",
        "unknown",
    ]
    confidence: float
    category: str = "general"
    customer_intent: str
    next_action: Literal["extract", "manual_review", "reject"]
    reasons: list[str] = Field(default_factory=list)


class FieldExtraction(BaseModel):
    field_name: str
    value: str | None = None
    confidence: float
    source_page: int | None = None
    evidence: str | None = None


class ExtractionOutput(BaseModel):
    document_id: str
    document_type: str
    fields: list[FieldExtraction]
    structured_fields: dict[str, Any] = Field(default_factory=dict)
    tables: list[dict[str, Any]] = Field(default_factory=list)
    handwritten_fields: dict[str, Any] = Field(default_factory=dict)
    confidence_map: dict[str, float] = Field(default_factory=dict)
    missing_fields: list[str] = Field(default_factory=list)
    next_action: Literal["validate", "manual_review"]
    reasons: list[str] = Field(default_factory=list)


class ValidationCheck(BaseModel):
    check_name: str
    status: Literal["passed", "failed", "warning"]
    message: str
    severity: Literal["low", "medium", "high"]


class ValidationOutput(BaseModel):
    document_id: str
    overall_status: Literal["approved", "needs_review", "rejected"]
    is_valid: bool = True
    risk_score: float
    confidence: float = 0.0
    checks: list[ValidationCheck]
    issues: list[ValidationCheck] = Field(default_factory=list)
    next_action: Literal["route", "manual_review", "exception"]
    reasons: list[str] = Field(default_factory=list)


class RoutingOutput(BaseModel):
    document_id: str
    destination_queue: Literal["auto_approve", "operations_review", "fraud_review", "compliance_review", "customer_follow_up"]
    next_step: Literal["approve", "route_to_review", "archive", "escalate"] = "approve"
    assigned_to: str = "automation"
    reason: str = "Policy and confidence thresholds satisfied."
    sla_minutes: int
    next_action: Literal["complete", "manual_review", "exception"]
    reasons: list[str] = Field(default_factory=list)


class ExceptionOutput(BaseModel):
    document_id: str
    exception_type: Literal["low_quality", "missing_data", "policy_conflict", "suspected_fraud", "system_error"]
    suggested_fix: str = "Escalate to operations review."
    escalation_level: Literal["low", "medium", "high"] = "medium"
    resolution_strategy: str
    requires_human_review: bool = True
    next_action: Literal["manual_review", "complete"] = "manual_review"
    reasons: list[str] = Field(default_factory=list)


class ReviewOutput(BaseModel):
    document_id: str
    review_id: str | None = None
    review_required: bool
    assigned_team: Literal["operations", "fraud", "compliance", "customer_support"]
    instructions: str
    due_in_minutes: int
    review_status: Literal["pending", "await_human", "completed"] = "pending"
    reviewer_feedback: str | None = None
    next_action: Literal["await_human", "complete"]
    reasons: list[str] = Field(default_factory=list)


class AuditOutput(BaseModel):
    document_id: str
    workflow_status: Literal["completed", "pending_review", "rejected"]
    audit_summary: str
    timeline: list[dict[str, Any]] = Field(default_factory=list)
    searchable_summary: str
    audit_entry: dict[str, Any] | None = None


class WorkflowState(BaseModel):
    document_id: str
    ingestion: IngestionOutput | None = None
    preprocessing: PreprocessingOutput | None = None
    classification: ClassificationOutput | None = None
    extraction: ExtractionOutput | None = None
    validation: ValidationOutput | None = None
    routing: RoutingOutput | None = None
    exception: ExceptionOutput | None = None
    review: ReviewOutput | None = None
    audit: AuditOutput | None = None
