from __future__ import annotations

from django.dispatch import receiver

from services.mongodb import mongo_service

from .events import agent_stage_completed


@receiver(agent_stage_completed)
def handle_agent_stage_completed(sender, document_id: str, stage: str, payload: dict, **kwargs):
    mongo_service.append_audit_log(
        document_id,
        f"agent.{stage}.completed",
        {
            "stage": stage,
            "payload": payload,
        },
    )
