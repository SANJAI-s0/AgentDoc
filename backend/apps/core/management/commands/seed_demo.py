from __future__ import annotations

from uuid import uuid4

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

from services.minio_client import minio_storage
from services.mongodb import mongo_service
from services.vector_search import vector_search_service


class Command(BaseCommand):
    help = "Seed demo users, documents, reviews, and audit logs into MongoDB and MinIO."

    def add_arguments(self, parser):
        parser.add_argument("--skip-if-present", action="store_true")
        parser.add_argument("--skip-storage", action="store_true")

    def handle(self, *args, **options):
        vector_search_service.ensure_indexes()
        self._seed_auth_users()

        users = [
            {
                "user_id": "cust_1001",
                "auth_username": "customer_demo",
                "display_name": "Customer Demo",
                "email": "customer.one@example.com",
                "role": "customer",
                "preferences": {"language": "en"},
            },
            {
                "user_id": "ops_reviewer_1",
                "auth_username": "reviewer_demo",
                "display_name": "Reviewer Demo",
                "email": "operations@example.com",
                "role": "reviewer",
                "team": "operations",
            },
        ]
        for user in users:
            mongo_service.upsert_one("users", {"user_id": user["user_id"]}, user)

        if options["skip_if_present"] and mongo_service.find_one("documents", {}):
            self.stdout.write(self.style.WARNING("Demo documents already present. Skipping document seed."))
            self.stdout.write(self.style.SUCCESS("Demo login accounts ensured: customer_demo / DemoPass123! and reviewer_demo / DemoPass123!"))
            return

        demo_documents = [
            {
                "document_id": "doc_demo_invoice_001",
                "user_id": "cust_1001",
                "title": "Electricity Bill March 2026",
                "file_name": "electricity-bill.pdf",
                "mime_type": "application/pdf",
                "storage_path": "incoming/doc_demo_invoice_001/electricity-bill.pdf",
                "source_channel": "web",
                "status": "completed",
                "document_type": "invoice",
                "checksum": f"seed-{uuid4().hex}",
                "page_count": 1,
                "raw_text": "Invoice No INV-1001 Date 2026-03-12 Total 2450.00",
                "searchable_summary": "Invoice processed and auto-approved for March electricity bill.",
            },
            {
                "document_id": "doc_demo_kyc_001",
                "user_id": "cust_1001",
                "title": "Handwritten KYC Address Form",
                "file_name": "kyc-address-form.jpg",
                "mime_type": "image/jpeg",
                "storage_path": "incoming/doc_demo_kyc_001/kyc-address-form.jpg",
                "source_channel": "mobile",
                "status": "pending_review",
                "document_type": "kyc_form",
                "checksum": f"seed-{uuid4().hex}",
                "page_count": 1,
                "raw_text": "Customer name Sam Taylor address handwritten partial match",
                "searchable_summary": "KYC form flagged for manual address verification.",
            },
        ]

        for document in demo_documents:
            if not options["skip_storage"]:
                try:
                    minio_storage.upload_bytes(
                        document["storage_path"],
                        content=f"Demo file for {document['document_id']}".encode("utf-8"),
                        content_type=document["mime_type"],
                    )
                except Exception as exc:
                    raise CommandError(
                        "MinIO is not reachable for demo file upload. "
                        "Start MinIO and retry, or run `python manage.py seed_demo --skip-storage` "
                        f"to seed MongoDB-only demo data.\nOriginal error: {exc}"
                    ) from exc
            mongo_service.upsert_one("documents", {"document_id": document["document_id"]}, document)

        mongo_service.upsert_one(
            "extractions",
            {"document_id": "doc_demo_invoice_001"},
            {
                "document_id": "doc_demo_invoice_001",
                "document_type": "invoice",
                "fields": [
                    {"field_name": "invoice_number", "value": "INV-1001", "confidence": 0.98, "source_page": 1, "evidence": "Invoice No INV-1001"},
                    {"field_name": "invoice_date", "value": "2026-03-12", "confidence": 0.97, "source_page": 1, "evidence": "Date 2026-03-12"},
                    {"field_name": "total_amount", "value": "2450.00", "confidence": 0.96, "source_page": 1, "evidence": "Total 2450.00"},
                ],
                "missing_fields": [],
                "next_action": "validate",
                "reasons": ["Seeded high-confidence invoice extraction."],
            },
        )

        mongo_service.upsert_one(
            "validation_results",
            {"document_id": "doc_demo_invoice_001"},
            {
                "document_id": "doc_demo_invoice_001",
                "overall_status": "approved",
                "risk_score": 0.11,
                "checks": [
                    {"check_name": "required_fields", "status": "passed", "message": "All mandatory fields found.", "severity": "medium"},
                    {"check_name": "duplicate_check", "status": "passed", "message": "No duplicate bill detected.", "severity": "low"},
                ],
                "next_action": "route",
                "reasons": ["Seeded validation case approved automatically."],
            },
        )

        mongo_service.upsert_one(
            "reviews",
            {"document_id": "doc_demo_kyc_001"},
            {
                "document_id": "doc_demo_kyc_001",
                "review_required": True,
                "assigned_team": "operations",
                "reviewer_email": "operations@example.com",
                "instructions": "Review the handwritten address and confirm it matches the customer profile.",
                "next_action": "await_human",
                "decision": None,
                "due_in_minutes": 30,
            },
        )

        audit_events = [
            ("doc_demo_invoice_001", "seed.document_loaded", {"status": "completed"}),
            ("doc_demo_kyc_001", "seed.document_loaded", {"status": "pending_review"}),
        ]
        for document_id, event_type, payload in audit_events:
            mongo_service.append_audit_log(document_id, event_type, payload)

        self.stdout.write(self.style.SUCCESS("Demo data seeded successfully."))
        self.stdout.write(self.style.SUCCESS("Demo login accounts: customer_demo / DemoPass123! and reviewer_demo / DemoPass123!"))

    def _seed_auth_users(self):
        user_model = get_user_model()
        auth_users = [
            {
                "username": "customer_demo",
                "email": "customer.one@example.com",
                "password": "DemoPass123!",
                "first_name": "Customer",
                "last_name": "Demo",
                "is_staff": False,
            },
            {
                "username": "reviewer_demo",
                "email": "operations@example.com",
                "password": "DemoPass123!",
                "first_name": "Reviewer",
                "last_name": "Demo",
                "is_staff": True,
            },
        ]
        for item in auth_users:
            user, created = user_model.objects.get_or_create(
                username=item["username"],
                defaults={
                    "email": item["email"],
                    "first_name": item["first_name"],
                    "last_name": item["last_name"],
                    "is_staff": item["is_staff"],
                },
            )
            if not created:
                user.email = item["email"]
                user.first_name = item["first_name"]
                user.last_name = item["last_name"]
                user.is_staff = item["is_staff"]
            user.set_password(item["password"])
            user.save()
