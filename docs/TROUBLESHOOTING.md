# Troubleshooting

## Upload fails with CORS error
- Ensure frontend origin is listed in:
  - `DJANGO_CORS_ALLOWED_ORIGINS`
  - `DJANGO_CSRF_TRUSTED_ORIGINS`
- Ensure MinIO/S3 bucket CORS allows `PUT`, `GET`, `HEAD` and headers `Authorization`, `Content-Type`.

## Documents remain in `processing`
- Verify `GEMINI_API_KEY` and `GEMINI_MODEL` are set correctly.
- Check backend logs for CrewAI or OCR fallback exceptions.
- Confirm MongoDB is reachable from backend container/runtime.

## Review emails not being sent
- Verify `SMTP_HOST` and `SMTP_PORT`.
- Check `DEFAULT_FROM_EMAIL` format and SMTP relay restrictions.
- Confirm `REVIEW_PORTAL_URL` points to the frontend review route.

## Semantic search returns no useful results
- Ensure `documents.vector_embedding` is populated.
- Confirm `EMBEDDING_VECTOR_DIMENSIONS` matches your stored vectors.
- If vector index is unavailable, enable fallback mode and verify text payload quality.

## Local setup sanity check
Run:
```powershell
.\.venv\Scripts\python.exe backend\scripts\preflight_check.py
```
This command validates env keys, service reachability, and basic project readiness.
