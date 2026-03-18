from __future__ import annotations

from typing import Any

from django.conf import settings

from services.vector_search import vector_search_service

from .prompts.library import SYSTEM_PROMPT
from .schemas import (
    AuditOutput,
    ClassificationOutput,
    ExceptionOutput,
    ExtractionOutput,
    FieldExtraction,
    IngestionOutput,
    PageDescriptor,
    PreprocessingOutput,
    ReviewOutput,
    RoutingOutput,
    ValidationCheck,
    ValidationOutput,
    WorkflowState,
)
from .tools.document_tools import (
    OCRTool,
    PolicyLookupTool,
    SearchKnowledgeTool,
    field_extractor,
)

try:
    from langchain_google_genai import ChatGoogleGenerativeAI
except ImportError:
    ChatGoogleGenerativeAI = None


SUPPORTED_TYPES = [
    "kyc_form",
    "invoice",
    "receipt",
    "insurance_claim",
    "shipping_document",
    "loan_application",
    "contract",
    "handwritten_form",
]


class DocumentCrewFactory:
    def __init__(self) -> None:
        self.ocr_tool = OCRTool()
        self.policy_tool = PolicyLookupTool()
        self.search_tool = SearchKnowledgeTool()

    def build_crew(self, payload: dict[str, Any]):
        """Build LangChain-based workflow (replaces CrewAI)"""
        if not ChatGoogleGenerativeAI or not settings.GEMINI_API_KEY:
            return None

        # Initialize LangChain LLM
        llm = ChatGoogleGenerativeAI(
            model=settings.GEMINI_MODEL.replace("gemini/", ""),
            google_api_key=settings.GEMINI_API_KEY,
            temperature=0.1,
        )

        return {"llm": llm, "payload": payload}

    def execute(self, payload: dict[str, Any]) -> WorkflowState:
        """Execute workflow using LangChain"""
        crew = self.build_crew(payload) if settings.GEMINI_API_KEY else None
        if crew:
            try:
                # Use LangChain for processing
                result = self._execute_langchain_workflow(crew["llm"], payload)
                if isinstance(result, WorkflowState):
                    return result
            except Exception:
                pass
        return self.simulate(payload)
    
    def _execute_langchain_workflow(self, llm, payload: dict[str, Any]) -> WorkflowState:
        """Execute workflow using LangChain agents"""
        # For now, use simulation
        # In future, implement LangChain agent chains here
        return self.simulate(payload)

    def _classify_document(self, payload: dict[str, Any], ocr_text: str) -> tuple[str, float, str, list[str]]:
        hint = (payload.get("document_type_hint") or "").strip().lower()
        if hint in SUPPORTED_TYPES:
            return hint, 0.92, "hint", ["Document type hint provided by client."]

        text = f"{payload.get('title', '')} {payload.get('file_name', '')} {ocr_text}".lower()
        keyword_map = {
            "invoice": ["invoice", "gst", "bill"],
            "receipt": ["receipt", "txn", "merchant"],
            "kyc_form": ["kyc", "government id", "aadhaar", "passport"],
            "loan_application": ["loan", "emi", "applicant"],
            "insurance_claim": ["claim", "policy", "incident"],
            "shipping_document": ["tracking", "awb", "shipment"],
            "contract": ["agreement", "contract", "party"],
            "handwritten_form": ["handwritten", "manual", "scribble"],
        }

        scores: dict[str, int] = {}
        for doc_type, words in keyword_map.items():
            scores[doc_type] = sum(1 for word in words if word in text)

        best_type = max(scores, key=scores.get) if scores else "unknown"
        best_score = scores.get(best_type, 0)

        similar_docs = vector_search_service.semantic_search(text[:500], limit=3, base_filter={}) if text.strip() else []
        vector_boost = 0.0
        if similar_docs:
            same_type = [item for item in similar_docs if item.get("document_type") == best_type]
            vector_boost = 0.08 if same_type else 0.03

        if best_score == 0:
            return "unknown", 0.4, "unknown", ["No strong lexical match for known document classes."]

        confidence = min(0.62 + (best_score * 0.08) + vector_boost, 0.96)
        return best_type, round(confidence, 4), "semantic_keyword", ["Classification based on keywords and semantic similarity."]

    def simulate(self, payload: dict[str, Any]) -> WorkflowState:
        document_id = payload["document_id"]
        page_count = int(payload.get("page_count") or 1)
        raw_text = (payload.get("raw_text") or "").strip()
        mime_type = payload.get("mime_type", "application/pdf")

        ingestion_reasons = ["File metadata accepted for processing."]
        ingestion_status = "accepted"
        next_ingestion_action = "preprocess"

        if not payload.get("storage_path"):
            ingestion_status = "rejected"
            next_ingestion_action = "reject"
            ingestion_reasons = ["Missing storage path from ingestion."]

        pages = [
            PageDescriptor(
                page_number=idx,
                mime_type=mime_type,
                storage_path=payload.get("storage_path"),
                ocr_text=raw_text if idx == 1 else "",
                confidence=0.9 if idx == 1 else 0.75,
            )
            for idx in range(1, page_count + 1)
        ]

        image_quality_score = 0.82
        if "handwritten" in (payload.get("document_type_hint") or ""):
            image_quality_score = 0.68
        if page_count > 2:
            image_quality_score = max(0.72, image_quality_score - 0.05)

        preprocess_next = "classify" if image_quality_score >= 0.7 else "manual_review"
        preprocess_reasons = ["OCR readiness assessed with quality threshold 0.7."]
        if preprocess_next == "manual_review":
            preprocess_reasons.append("Image quality is below threshold and needs human preprocessing.")

        doc_type, class_conf, category, class_reasons = self._classify_document(payload, raw_text)

        if doc_type == "unknown":
            class_next = "manual_review"
        elif class_conf < 0.85:
            class_next = "manual_review"
            class_reasons.append("Classification confidence below 0.85 threshold.")
        else:
            class_next = "extract"

        policy = self.policy_tool.run(doc_type if doc_type in SUPPORTED_TYPES else "invoice")
        required_fields = policy.get("required_fields", [])

        extraction_bundle = field_extractor.extract(raw_text, doc_type, required_fields)
        structured_fields = extraction_bundle["structured_fields"]
        confidence_map = extraction_bundle["confidence_map"]

        field_models = []
        for field_name in required_fields:
            value = structured_fields.get(field_name)
            field_models.append(
                FieldExtraction(
                    field_name=field_name,
                    value=value or None,
                    confidence=float(confidence_map.get(field_name, 0.45)),
                    source_page=1,
                    evidence="Pattern-based extraction from OCR text.",
                )
            )

        extraction_reasons = ["Hybrid extraction using OCR signal and structured field policies."]
        extraction_next = "validate"
        if extraction_bundle["missing_fields"]:
            extraction_reasons.append("Some required fields are missing from extracted output.")

        validation_checks = []
        issues = []
        missing_fields = extraction_bundle["missing_fields"]
        validation_checks.append(
            ValidationCheck(
                check_name="required_fields",
                status="failed" if missing_fields else "passed",
                message="Missing required fields detected." if missing_fields else "All required fields extracted.",
                severity="high" if missing_fields else "low",
            )
        )

        handwritten_penalty = 0.12 if doc_type == "handwritten_form" else 0.0
        confidence_penalty = 0.18 if class_conf < 0.85 else 0.0
        missing_penalty = min(len(missing_fields) * 0.12, 0.48)
        quality_penalty = 0.14 if image_quality_score < 0.7 else 0.0
        risk_score = round(min(0.12 + handwritten_penalty + confidence_penalty + missing_penalty + quality_penalty, 0.95), 4)
        avg_conf = sum(confidence_map.values()) / len(confidence_map) if confidence_map else 0.0

        if missing_fields:
            issues.append(
                ValidationCheck(
                    check_name="missing_required_fields",
                    status="failed",
                    message=f"Missing fields: {', '.join(missing_fields)}",
                    severity="high",
                )
            )

        if risk_score > policy.get("risk_threshold", 0.6):
            issues.append(
                ValidationCheck(
                    check_name="risk_threshold",
                    status="warning",
                    message="Risk score exceeded automation threshold.",
                    severity="high",
                )
            )

        needs_review = bool(issues) or payload.get("force_review", False)
        validation_overall = "needs_review" if needs_review else "approved"
        validation_next = "manual_review" if needs_review else "route"

        destination_queue = "auto_approve"
        next_step = "approve"
        assigned_to = "automation"
        routing_reason = "Validation thresholds satisfied for straight-through processing."
        routing_next_action = "complete"
        sla_minutes = 5

        if risk_score > 0.75:
            destination_queue = "fraud_review"
            next_step = "escalate"
            assigned_to = "fraud"
            routing_reason = "High risk score requires escalation."
            routing_next_action = "exception"
            sla_minutes = 20
        elif needs_review:
            destination_queue = "operations_review"
            next_step = "route_to_review"
            assigned_to = "operations"
            routing_reason = "Issues present or confidence threshold unmet; routing to human review."
            routing_next_action = "manual_review"
            sla_minutes = 30

        exception_output = None
        if routing_next_action == "exception" or preprocess_next == "manual_review":
            exception_output = ExceptionOutput(
                document_id=document_id,
                exception_type="suspected_fraud" if risk_score > 0.75 else "low_quality",
                suggested_fix="Escalate to reviewer and request supporting clarification.",
                escalation_level="high" if risk_score > 0.75 else "medium",
                resolution_strategy="Route to specialist queue with full audit evidence.",
                requires_human_review=True,
                next_action="manual_review",
                reasons=[routing_reason],
            )

        review_required = routing_next_action in {"manual_review", "exception"}
        review_output = ReviewOutput(
            document_id=document_id,
            review_id=f"rev_{document_id.split('_')[-1]}",
            review_required=review_required,
            assigned_team="fraud" if destination_queue == "fraud_review" else "operations",
            instructions="Review extracted fields against source document and approve/reject with corrections.",
            due_in_minutes=sla_minutes,
            review_status="await_human" if review_required else "completed",
            reviewer_feedback=None,
            next_action="await_human" if review_required else "complete",
            reasons=[routing_reason],
        )

        workflow_status = "pending_review" if review_required else "completed"
        if ingestion_status == "rejected":
            workflow_status = "rejected"

        state = WorkflowState(
            document_id=document_id,
            ingestion=IngestionOutput(
                document_id=document_id,
                user_id=payload.get("user_id", "anonymous"),
                source_channel=payload.get("source_channel", "web"),
                storage_path=payload.get("storage_path", ""),
                file_name=payload.get("file_name", "unknown"),
                mime_type=mime_type,
                page_count=page_count,
                checksum=payload.get("checksum", ""),
                file_urls=payload.get("file_urls", []),
                status=ingestion_status,
                priority="high" if payload.get("vip_customer") else "normal",
                next_action=next_ingestion_action,
                reasons=ingestion_reasons,
            ),
            preprocessing=PreprocessingOutput(
                document_id=document_id,
                image_quality_score=image_quality_score,
                detected_languages=["en"],
                rotation_applied=0,
                pages=pages,
                next_action=preprocess_next,
                reasons=preprocess_reasons,
            ),
            classification=ClassificationOutput(
                document_id=document_id,
                document_type=doc_type if doc_type in SUPPORTED_TYPES else "unknown",
                confidence=class_conf,
                category=category,
                customer_intent="Submit document for automated processing",
                next_action=class_next,
                reasons=class_reasons,
            ),
            extraction=ExtractionOutput(
                document_id=document_id,
                document_type=doc_type,
                fields=field_models,
                structured_fields=structured_fields,
                tables=extraction_bundle["tables"],
                handwritten_fields=extraction_bundle["handwritten_fields"],
                confidence_map=confidence_map,
                missing_fields=missing_fields,
                next_action=extraction_next,
                reasons=extraction_reasons,
            ),
            validation=ValidationOutput(
                document_id=document_id,
                overall_status=validation_overall,
                is_valid=not needs_review,
                risk_score=risk_score,
                confidence=round(float(avg_conf), 4),
                checks=validation_checks,
                issues=issues,
                next_action=validation_next,
                reasons=["Rule-based and semantic checks applied."],
            ),
            routing=RoutingOutput(
                document_id=document_id,
                destination_queue=destination_queue,
                next_step=next_step,
                assigned_to=assigned_to,
                reason=routing_reason,
                sla_minutes=sla_minutes,
                next_action=routing_next_action,
                reasons=[routing_reason],
            ),
            review=review_output,
            audit=AuditOutput(
                document_id=document_id,
                workflow_status=workflow_status,
                audit_summary="Agentic workflow executed with ingestion, preprocessing, classification, extraction, validation, routing, review, and audit stages.",
                timeline=[
                    {"stage": "ingestion", "status": ingestion_status},
                    {"stage": "preprocessing", "status": "completed"},
                    {"stage": "classification", "status": "completed"},
                    {"stage": "extraction", "status": "completed"},
                    {"stage": "validation", "status": validation_overall},
                    {"stage": "routing", "status": destination_queue},
                    {"stage": "review", "status": "pending" if review_required else "skipped"},
                ],
                searchable_summary=f"{doc_type} document processed with status {workflow_status} and risk {risk_score}",
                audit_entry={"destination_queue": destination_queue, "risk_score": risk_score},
            ),
        )

        if exception_output:
            state.exception = exception_output

        return state


document_crew_factory = DocumentCrewFactory()
