from __future__ import annotations

import mimetypes
import os
from collections import Counter
from io import BytesIO
from typing import Any
from uuid import uuid4

from bson import ObjectId
from django.contrib.auth import authenticate
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from apps.agents.runner import execute_document_workflow
from apps.agents.tools.document_tools import HashTool
from apps.reviews.services import trigger_review_workflow
from services.minio_client import minio_storage
from services.mongodb import mongo_service
from services.vector_search import vector_search_service

from .serializers import (
    DocumentCreateSerializer,
    LoginSerializer,
    ReviewActionSerializer,
    ReviewSubmitSerializer,
    SearchSerializer,
    TokenRefreshSerializer,
    TriggerReviewSerializer,
    UploadUrlSerializer,
)

try:
    from pypdf import PdfReader
except Exception:  # pragma: no cover
    PdfReader = None

try:
    from PIL import Image
except Exception:  # pragma: no cover
    Image = None


hash_tool = HashTool()
REVIEWER_ROLES = {"reviewer", "admin"}
SUPPORTED_MIME_PREFIXES = ("image/", "text/")
SUPPORTED_EXACT_MIME = {"application/pdf"}


def _serialize(value: Any):
    if isinstance(value, ObjectId):
        return str(value)
    if isinstance(value, list):
        return [_serialize(item) for item in value]
    if isinstance(value, dict):
        return {key: _serialize(item) for key, item in value.items()}
    return value


def _profile_for_user(user):
    if not user or not user.is_authenticated:
        return None
    profile = mongo_service.find_one("users", {"auth_username": user.username})
    if profile:
        return profile
    if user.email:
        return mongo_service.find_one("users", {"email": user.email})
    return None


def _identity_for_request(request):
    user = getattr(request, "user", None)
    if not user or not user.is_authenticated:
        return None
    profile = _profile_for_user(user) or {}
    return {
        "username": user.username,
        "email": user.email,
        "display_name": user.get_full_name() or profile.get("display_name") or user.username,
        "user_id": profile.get("user_id") or user.username,
        "role": profile.get("role") or ("admin" if user.is_staff else "customer"),
        "team": profile.get("team"),
    }


def _issue_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        "access": str(refresh.access_token),
        "refresh": str(refresh),
        "token_type": "Bearer",
    }


def _auth_response(identity, tokens: dict[str, str] | None = None):
    payload = {
        "authenticated": True,
        "user": {
            "username": identity["username"],
            "email": identity["email"],
            "display_name": identity["display_name"],
            "user_id": identity["user_id"],
            "role": identity["role"],
            "team": identity["team"],
        },
    }
    if tokens:
        payload.update(tokens)
    return payload


def _require_identity(request):
    identity = _identity_for_request(request)
    if identity is None:
        return None, Response({"detail": "Authentication required."}, status=status.HTTP_401_UNAUTHORIZED)
    return identity, None


def _can_review(identity):
    return identity["role"] in REVIEWER_ROLES


def _document_scope(identity):
    if _can_review(identity):
        return {}
    return {"user_id": identity["user_id"]}


def _next_review_id() -> str:
    return f"rev_{uuid4().hex[:12]}"


def _is_supported_file(mime_type: str, file_name: str) -> bool:
    guessed, _ = mimetypes.guess_type(file_name or "")
    effective_mime = (mime_type or guessed or "application/octet-stream").lower()
    if effective_mime in SUPPORTED_EXACT_MIME:
        return True
    return any(effective_mime.startswith(prefix) for prefix in SUPPORTED_MIME_PREFIXES)


def _estimate_page_count(content: bytes, mime_type: str, file_name: str) -> int:
    if not content:
        return 1

    effective_mime = (mime_type or "").lower()
    if effective_mime == "application/pdf" or (file_name or "").lower().endswith(".pdf"):
        if PdfReader is None:
            return 1
        try:
            reader = PdfReader(BytesIO(content))
            return max(len(reader.pages), 1)
        except Exception:
            return 1

    if effective_mime.startswith("image/") and Image is not None:
        try:
            image = Image.open(BytesIO(content))
            return max(int(getattr(image, "n_frames", 1)), 1)
        except Exception:
            return 1

    return 1


class HealthView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        index_state = vector_search_service.ensure_indexes()
        return Response({"status": "ok", "vector_search": index_state})


@method_decorator(ensure_csrf_cookie, name="dispatch")
class CsrfView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({"detail": "CSRF cookie set"})


class SessionView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        identity = _identity_for_request(request)
        if identity is None:
            return Response({"authenticated": False})
        return Response(_auth_response(identity))


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(
            request,
            username=serializer.validated_data["username"],
            password=serializer.validated_data["password"],
        )
        if user is None:
            return Response({"detail": "Invalid username or password."}, status=status.HTTP_400_BAD_REQUEST)
        identity = _identity_for_request(type("obj", (object,), {"user": user})())
        if identity is None:
            return Response({"detail": "Unable to resolve user profile."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(_auth_response(identity, _issue_tokens_for_user(user)))


class TokenRefreshView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = TokenRefreshSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            refresh = RefreshToken(serializer.validated_data["refresh"])
        except Exception:
            return Response({"detail": "Invalid refresh token."}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"access": str(refresh.access_token), "token_type": "Bearer"})


class LogoutView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        refresh_token = request.data.get("refresh")
        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
            except Exception:
                pass
        return Response({"authenticated": False})


class DashboardView(APIView):
    def get(self, request):
        identity, error = _require_identity(request)
        if error:
            return error

        document_query = _document_scope(identity)
        documents = mongo_service.find_many("documents", document_query, limit=200, sort=[("updated_at", -1)])
        reviews = []
        if _can_review(identity):
            reviews = mongo_service.find_many("reviews", {}, limit=100, sort=[("updated_at", -1)])

        status_counts = Counter(doc.get("status", "unknown") for doc in documents)
        return Response(
            {
                "documents_total": len(documents),
                "reviews_open": sum(1 for review in reviews if review.get("next_action") == "await_human"),
                "status_breakdown": dict(status_counts),
                "recent_documents": _serialize(documents[:5]),
                "current_user": _auth_response(identity)["user"],
            }
        )


class DocumentUploadUrlView(APIView):
    def post(self, request):
        identity, error = _require_identity(request)
        if error:
            return error

        serializer = UploadUrlSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        file_name = serializer.validated_data["file_name"]
        mime_type = serializer.validated_data["mime_type"]

        if not _is_supported_file(mime_type, file_name):
            return Response(
                {"detail": "Unsupported file type. Supported: PDF, image, and text."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        document_id = f"doc_{uuid4().hex[:12]}"
        object_name = f"incoming/{document_id}/{file_name}"

        upload_url = minio_storage.presigned_put_url(object_name, expires_minutes=30)
        file_url = minio_storage.presigned_get_url(object_name, expires_minutes=120)

        mongo_service.insert_one(
            "audit_logs",
            {
                "document_id": document_id,
                "event_type": "document.presigned_upload_issued",
                "payload": {
                    "file_name": file_name,
                    "mime_type": mime_type,
                    "object_name": object_name,
                    "issued_to": identity["username"],
                },
            },
        )

        return Response(
            {
                "document_id": document_id,
                "object_name": object_name,
                "upload_url": upload_url,
                "file_url": file_url,
                "expires_in_minutes": 30,
            }
        )

class DocumentListCreateView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request):
        identity, error = _require_identity(request)
        if error:
            return error
        documents = mongo_service.find_many("documents", _document_scope(identity), limit=100, sort=[("updated_at", -1)])
        return Response(_serialize(documents))

    def post(self, request):
        identity, error = _require_identity(request)
        if error:
            return error

        serializer = DocumentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated = serializer.validated_data

        document_id = f"doc_{uuid4().hex[:12]}"
        upload = validated.get("file")
        minio_object_name = (validated.get("minio_object_name") or "").strip()
        uploaded_via_presigned = validated.get("uploaded_via_presigned", False)

        content = b""
        mime_type = validated.get("mime_type") or "application/pdf"
        file_name = validated.get("file_name")
        storage_path = ""

        if upload:
            file_name = file_name or getattr(upload, "name", f"document-{uuid4()}.pdf")
            mime_type = validated.get("mime_type") or getattr(upload, "content_type", "application/pdf")
            content = upload.read()
            storage_path = f"incoming/{document_id}/{file_name}"
        elif minio_object_name and uploaded_via_presigned:
            storage_path = minio_object_name
            file_name = file_name or minio_object_name.split("/")[-1]
            path_parts = minio_object_name.split("/")
            if len(path_parts) > 1 and path_parts[1].startswith("doc_"):
                document_id = path_parts[1]
            guessed_mime, _ = mimetypes.guess_type(file_name)
            mime_type = mime_type or guessed_mime or "application/octet-stream"
            try:
                minio_storage.stat(storage_path)
                content = minio_storage.download_bytes(storage_path)
            except Exception as exc:
                return Response(
                    {"detail": f"Unable to access presigned upload object in MinIO. {exc}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            return Response(
                {"detail": "Provide either multipart `file` or (`minio_object_name` + `uploaded_via_presigned=true`)."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not _is_supported_file(mime_type, file_name or ""):
            return Response(
                {"detail": "Unsupported file type. Supported: PDF, image, and text."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if upload:
            try:
                minio_storage.upload_bytes(storage_path, content, content_type=mime_type)
            except Exception as exc:
                return Response(
                    {"detail": f"Document storage unavailable. Check MinIO connection and credentials. {exc}"},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE,
                )

        checksum = hash_tool.run(content) if content else hash_tool.run(storage_path.encode("utf-8"))
        duplicate = mongo_service.find_one("documents", {"checksum": checksum})
        if duplicate and duplicate.get("status") not in {"rejected", "failed"}:
            mongo_service.append_audit_log(
                duplicate.get("document_id", "unknown"),
                "ingestion.duplicate_detected",
                {
                    "checksum": checksum,
                    "source_user": identity["username"],
                    "source_channel": validated.get("source_channel", "web"),
                },
            )
            return Response(
                {
                    "detail": "Duplicate document detected.",
                    "duplicate_document_id": duplicate.get("document_id"),
                },
                status=status.HTTP_409_CONFLICT,
            )

        effective_user_id = identity["user_id"]
        if _can_review(identity) and validated.get("user_id"):
            effective_user_id = validated["user_id"]

        page_count = _estimate_page_count(content, mime_type, file_name or "")
        file_url = ""
        try:
            file_url = minio_storage.presigned_get_url(storage_path, expires_minutes=120)
        except Exception:
            file_url = storage_path

        record = {
            "document_id": document_id,
            "user_id": effective_user_id,
            "title": validated.get("title") or file_name,
            "file_name": file_name,
            "mime_type": mime_type,
            "storage_path": storage_path,
            "source_channel": validated["source_channel"],
            "status": "processing",
            "checksum": checksum,
            "page_count": page_count,
            "file_urls": [file_url] if file_url else [],
            "document_type_hint": validated.get("document_type_hint") or None,
            "vip_customer": validated.get("vip_customer", False),
            "force_review": validated.get("force_review", False),
            "raw_text": content.decode("utf-8", errors="ignore")[:5000] if content and mime_type.startswith("text/") else "",
            "submitted_by": identity["username"],
        }
        mongo_service.insert_one("documents", record)

        if validated.get("reviewer_email"):
            mongo_service.upsert_one(
                "reviews",
                {"document_id": document_id},
                {
                    "review_id": _next_review_id(),
                    "document_id": document_id,
                    "review_required": False,
                    "assigned_team": "operations",
                    "reviewer_email": validated["reviewer_email"],
                    "next_action": "pending_agent_decision",
                    "review_status": "pending",
                },
            )

        for page_number in range(1, page_count + 1):
            mongo_service.upsert_one(
                "pages",
                {"document_id": document_id, "page_number": page_number},
                {
                    "document_id": document_id,
                    "page_number": page_number,
                    "clean_image_url": file_url,
                    "ocr_text": "",
                },
            )

        mongo_service.append_audit_log(
            document_id,
            "document.processing_started",
            {
                "storage_path": storage_path,
                "submitted_by": identity["username"],
                "page_count": page_count,
            },
        )

        try:
            workflow_state = execute_document_workflow(record)
        except Exception as exc:
            mongo_service.update_one("documents", {"document_id": document_id}, {"status": "failed"})
            mongo_service.append_audit_log(document_id, "workflow.failed", {"reason": str(exc)[:400]})
            return Response(
                {"detail": f"Workflow failed for this document. {exc}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        latest_document = mongo_service.find_one("documents", {"document_id": document_id}) or record
        return Response(
            _serialize({"document": latest_document, "workflow": workflow_state.model_dump()}),
            status=status.HTTP_201_CREATED,
        )

class DocumentUploadView(DocumentListCreateView):
    """Alias endpoint for POST /api/documents/upload/."""


class DocumentDetailView(APIView):
    def get(self, request, document_id: str):
        identity, error = _require_identity(request)
        if error:
            return error

        document = mongo_service.find_one("documents", {"document_id": document_id})
        if not document:
            return Response({"detail": "Document not found."}, status=status.HTTP_404_NOT_FOUND)
        if not _can_review(identity) and document.get("user_id") != identity["user_id"]:
            return Response({"detail": "You do not have access to this document."}, status=status.HTTP_403_FORBIDDEN)

        extraction = mongo_service.find_one("extractions", {"document_id": document_id})
        validation = mongo_service.find_one("validation_results", {"document_id": document_id})
        pages = mongo_service.find_many("pages", {"document_id": document_id}, limit=100, sort=[("page_number", 1)])
        reviews = mongo_service.find_many("reviews", {"document_id": document_id}, limit=20, sort=[("updated_at", -1)])
        audit_logs = mongo_service.find_many("audit_logs", {"document_id": document_id}, limit=100, sort=[("updated_at", -1)])
        return Response(
            _serialize(
                {
                    "document": document,
                    "pages": pages,
                    "extraction": extraction,
                    "validation": validation,
                    "reviews": reviews,
                    "audit_logs": audit_logs,
                }
            )
        )


class DocumentStatusView(APIView):
    def get(self, request, document_id: str):
        identity, error = _require_identity(request)
        if error:
            return error

        document = mongo_service.find_one("documents", {"document_id": document_id})
        if not document:
            return Response({"detail": "Document not found."}, status=status.HTTP_404_NOT_FOUND)
        if not _can_review(identity) and document.get("user_id") != identity["user_id"]:
            return Response({"detail": "You do not have access to this document."}, status=status.HTTP_403_FORBIDDEN)

        return Response(
            _serialize(
                {
                    "document_id": document_id,
                    "status": document.get("status", "unknown"),
                    "document_type": document.get("document_type"),
                    "updated_at": document.get("updated_at"),
                }
            )
        )


class DocumentExtractionView(APIView):
    def get(self, request, document_id: str):
        identity, error = _require_identity(request)
        if error:
            return error

        document = mongo_service.find_one("documents", {"document_id": document_id})
        if not document:
            return Response({"detail": "Document not found."}, status=status.HTTP_404_NOT_FOUND)
        if not _can_review(identity) and document.get("user_id") != identity["user_id"]:
            return Response({"detail": "You do not have access to this document."}, status=status.HTTP_403_FORBIDDEN)

        extraction = mongo_service.find_one("extractions", {"document_id": document_id})
        if not extraction:
            return Response({"detail": "Extraction not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response(_serialize(extraction))


class ReviewQueueView(APIView):
    def get(self, request):
        identity, error = _require_identity(request)
        if error:
            return error
        if not _can_review(identity):
            return Response({"detail": "Reviewer access required."}, status=status.HTTP_403_FORBIDDEN)
        reviews = mongo_service.find_many("reviews", {}, limit=100, sort=[("updated_at", -1)])
        return Response(_serialize(reviews))


class ReviewActionView(APIView):
    def post(self, request, document_id: str):
        identity, error = _require_identity(request)
        if error:
            return error
        if not _can_review(identity):
            return Response({"detail": "Reviewer access required."}, status=status.HTTP_403_FORBIDDEN)

        serializer = ReviewActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        review = mongo_service.find_one("reviews", {"document_id": document_id})
        if not review:
            return Response({"detail": "Review not found."}, status=status.HTTP_404_NOT_FOUND)

        reviewer_id = data.get("reviewer_id") or identity["user_id"]
        payload = {
            "decision": data["decision"],
            "reviewer_id": reviewer_id,
            "reviewer_username": identity["username"],
            "comment": data.get("comment", ""),
            "next_action": "await_human" if data["decision"] == "request_changes" else "complete",
            "review_status": "pending" if data["decision"] == "request_changes" else "completed",
            "reviewer_feedback": data.get("comment", ""),
        }
        mongo_service.update_one("reviews", {"document_id": document_id}, payload)
        mongo_service.update_one(
            "documents",
            {"document_id": document_id},
            {"status": "completed" if data["decision"] == "approve" else "pending_review" if data["decision"] == "request_changes" else "rejected"},
        )
        mongo_service.append_audit_log(document_id, "review.completed", payload)
        return Response({"document_id": document_id, "decision": data["decision"]})


class ReviewSubmitView(APIView):
    def post(self, request, review_id: str):
        identity, error = _require_identity(request)
        if error:
            return error
        if not _can_review(identity):
            return Response({"detail": "Reviewer access required."}, status=status.HTTP_403_FORBIDDEN)

        serializer = ReviewSubmitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        review = mongo_service.find_one("reviews", {"review_id": review_id})
        if not review:
            review = mongo_service.find_one("reviews", {"document_id": review_id})
        if not review:
            return Response({"detail": "Review not found."}, status=status.HTTP_404_NOT_FOUND)

        document_id = review["document_id"]
        decision = data["decision"]
        review_payload = {
            "decision": decision,
            "review_status": "pending" if decision == "request_changes" else "completed",
            "reviewer_feedback": data.get("reviewer_feedback", ""),
            "corrected_fields": data.get("corrected_fields", {}),
            "reviewer_id": identity["user_id"],
            "reviewer_username": identity["username"],
            "next_action": "await_human" if decision == "request_changes" else "complete",
        }
        mongo_service.update_one("reviews", {"document_id": document_id}, review_payload)
        mongo_service.update_one(
            "documents",
            {"document_id": document_id},
            {"status": "completed" if decision == "approve" else "pending_review" if decision == "request_changes" else "rejected"},
        )
        mongo_service.append_audit_log(document_id, "review.submitted", review_payload)
        return Response({"review_id": review.get("review_id", review_id), "document_id": document_id, "decision": decision})


class TriggerReviewView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        identity = _identity_for_request(request)
        internal_token = request.headers.get("X-Agent-Internal-Token")
        token_allowed = bool(os.getenv("AGENT_INTERNAL_TOKEN")) and internal_token == os.getenv("AGENT_INTERNAL_TOKEN")

        if identity is None and not token_allowed:
            return Response({"detail": "Authentication required."}, status=status.HTTP_401_UNAUTHORIZED)

        if identity is not None and not _can_review(identity) and not token_allowed:
            return Response({"detail": "Reviewer access required."}, status=status.HTTP_403_FORBIDDEN)

        serializer = TriggerReviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        document = mongo_service.find_one("documents", {"document_id": data["document_id"]})
        if not document:
            return Response({"detail": "Document not found."}, status=status.HTTP_404_NOT_FOUND)

        result = trigger_review_workflow(
            document_id=data["document_id"],
            assigned_team=data["assigned_team"],
            reviewer_email=data.get("reviewer_email"),
            instructions=data.get("instructions"),
            due_in_minutes=30,
        )
        return Response(_serialize(result))


class SearchView(APIView):
    def get(self, request):
        identity, error = _require_identity(request)
        if error:
            return error
        serializer = SearchSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        query = serializer.validated_data.get("q", "")
        limit = serializer.validated_data["limit"]
        return Response(_serialize(vector_search_service.semantic_search(query, limit=limit, base_filter=_document_scope(identity))))


class SemanticSearchView(SearchView):
    """Alias endpoint for GET /api/search/semantic/."""


class AuditLogView(APIView):
    def get(self, request, document_id: str):
        identity, error = _require_identity(request)
        if error:
            return error

        document = mongo_service.find_one("documents", {"document_id": document_id})
        if not document:
            return Response({"detail": "Document not found."}, status=status.HTTP_404_NOT_FOUND)
        if not _can_review(identity) and document.get("user_id") != identity["user_id"]:
            return Response({"detail": "You do not have access to this document."}, status=status.HTTP_403_FORBIDDEN)

        logs = mongo_service.find_many("audit_logs", {"document_id": document_id}, limit=200, sort=[("updated_at", -1)])
        return Response(_serialize(logs))







