from __future__ import annotations

from django.conf import settings
from django.core.mail import send_mail


def send_review_email(to_email: str, document_id: str, review_id: str) -> None:
    review_link = f"{settings.REVIEW_PORTAL_URL}?reviewId={review_id}&documentId={document_id}"
    send_mail(
        subject=f"Document review required: {document_id}",
        message=f"A document needs human review. Open: {review_link}",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[to_email],
        fail_silently=False,
    )
