# API Reference

## Base URL
- Local: `http://localhost:8000/api`

## Authentication (JWT)
### `POST /api/auth/login/`
Returns `access` and `refresh` tokens plus user profile.

### `POST /api/auth/refresh/`
Returns a new `access` token.

### `GET /api/auth/me/`
Returns authenticated user profile when Bearer token is valid.

### `POST /api/auth/logout/`
Logs out and clears token state on frontend.

## Health and Dashboard
### `GET /api/health/`
Returns service health and vector-search strategy metadata.

### `GET /api/dashboard/`
Returns document and review metrics scoped to role.

## Documents
### `POST /api/documents/upload-url/`
Issues MinIO presigned upload URL.

Payload:
```json
{
  "file_name": "invoice.pdf",
  "mime_type": "application/pdf"
}
```

### `POST /api/documents/upload/`
Finalizes ingestion and triggers CrewAI workflow.

Supports:
1. Multipart direct upload (`file`)
2. Presigned finalize (`minio_object_name` + `uploaded_via_presigned=true`)

Example finalize payload fields:
- `source_channel`
- `file_name`
- `mime_type`
- `document_type_hint`
- `force_review`
- `minio_object_name`
- `uploaded_via_presigned`

### `GET /api/documents/`
Lists visible documents.

### `GET /api/documents/{document_id}/`
Returns document + pages + extraction + validation + reviews + audit logs.

### `GET /api/documents/{document_id}/status/`
Returns lightweight status payload.

### `GET /api/documents/{document_id}/extraction/`
Returns extraction record.

## Reviews
### `GET /api/reviews/`
Reviewer/admin queue.

### `POST /api/reviews/{document_id}/action/`
Decision by document id.

### `POST /api/reviews/{review_id}/submit/`
Decision + corrected fields by review id.

### `POST /api/trigger-review/`
Triggers HITL review workflow (reviewer/admin or agent internal token).

## Search and Audit
### `GET /api/search/semantic/?q=invoice+total&limit=10`
Vector search with Atlas-compatible vector stage + local fallback.

### `GET /api/audit/{document_id}/`
Returns ordered audit records.

## Authorization Header
```http
Authorization: Bearer <access-token>
```
