from __future__ import annotations

import logging

from django.conf import settings
from django.core.mail import send_mail

logger = logging.getLogger(__name__)


def send_review_email(to_email: str, document_id: str, review_id: str) -> bool:
    """Send review notification email. Returns True on success, False if SMTP unavailable."""
    review_link = (
        f"{settings.REVIEW_PORTAL_URL}?reviewId={review_id}&documentId={document_id}"
    )
    try:
        send_mail(
            subject=f"Document review required: {document_id}",
            message=f"A document needs human review.\n\nOpen review: {review_link}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[to_email],
            fail_silently=False,
        )
        logger.info("Review email sent to %s for document %s", to_email, document_id)
        return True
    except Exception as exc:
        # SMTP server not available in dev/local environments — log and continue
        logger.warning("Review email not sent (SMTP unavailable): %s", exc)
        return False
