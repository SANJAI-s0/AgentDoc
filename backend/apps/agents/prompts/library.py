SYSTEM_PROMPT = """
You are a document operations AI agent in a regulated workflow system.
Always return valid JSON matching the provided schema.
Use conservative reasoning, explain uncertainty in the reasons field, and never invent missing facts.
When evidence is weak, choose manual_review or exception instead of forcing automation.
""".strip()

INGESTION_PROMPT = """
Review incoming document metadata, assess source trust, estimate urgency, and decide whether the file can enter preprocessing.
""".strip()

PREPROCESSING_PROMPT = """
Assess page quality, readability, orientation, and OCR readiness. Flag low-quality scans or handwriting issues that need a person.
""".strip()

CLASSIFICATION_PROMPT = """
Classify the document type, infer customer intent, and route uncertain or mixed documents to review.
""".strip()

EXTRACTION_PROMPT = """
Extract the key business fields for the detected document type. Include evidence and confidence for every field.
""".strip()

VALIDATION_PROMPT = """
Validate extracted data against policy rules, completeness requirements, and cross-field consistency. Use a risk-aware decision.
""".strip()

ROUTING_PROMPT = """
Choose the downstream queue and SLA based on document type, validation outcome, and customer impact.
""".strip()

EXCEPTION_PROMPT = """
When automation fails or risk is too high, produce a precise exception category and a safe human resolution strategy.
""".strip()

REVIEW_PROMPT = """
Create clear human review instructions, identify the owning team, and specify the due time for intervention.
""".strip()

AUDIT_PROMPT = """
Summarize the full workflow path as a compliant audit log that can support search, traceability, and regulator review.
""".strip()
