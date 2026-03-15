from __future__ import annotations

from django.dispatch import Signal


agent_stage_completed = Signal()


def emit_agent_stage_completed(document_id: str, stage: str, payload: dict):
    agent_stage_completed.send(
        sender="apps.agents.workflow",
        document_id=document_id,
        stage=stage,
        payload=payload,
    )
