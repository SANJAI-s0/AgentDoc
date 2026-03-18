from __future__ import annotations

from typing import Any

from .crew import document_crew_factory
from .schemas import WorkflowState


class DocumentWorkflow:
    """LangChain-based document workflow (replaces CrewAI Flow)"""
    
    def __init__(self, payload: dict[str, Any]):
        self.payload = payload
        self.state: WorkflowState | None = None

    def kick_off(self) -> WorkflowState:
        """Execute the workflow"""
        self.state = document_crew_factory.execute(self.payload)
        return self.state

    def finalize(self, state: WorkflowState) -> WorkflowState:
        """Finalize the workflow"""
        self.state = state
        return state


def run_document_workflow_sync(payload: dict[str, Any]) -> WorkflowState:
    """Run document workflow synchronously"""
    workflow = DocumentWorkflow(payload)
    return workflow.kick_off()
