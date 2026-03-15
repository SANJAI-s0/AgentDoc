from __future__ import annotations

from typing import Any

from .crew import document_crew_factory
from .schemas import WorkflowState

try:
    from crewai.flow.flow import Flow, listen, start
except Exception:  # pragma: no cover
    Flow = object

    def start():
        def decorator(func):
            return func
        return decorator

    def listen(_event):
        def decorator(func):
            return func
        return decorator


class DocumentWorkflow(Flow):
    def __init__(self, payload: dict[str, Any]):
        super().__init__()
        self.payload = payload
        self.state: WorkflowState | None = None

    @start()
    def kick_off(self) -> WorkflowState:
        self.state = document_crew_factory.execute(self.payload)
        return self.state

    @listen(kick_off)
    def finalize(self, state: WorkflowState) -> WorkflowState:
        self.state = state
        return state


def run_document_workflow_sync(payload: dict[str, Any]) -> WorkflowState:
    workflow = DocumentWorkflow(payload)
    return workflow.kick_off()
