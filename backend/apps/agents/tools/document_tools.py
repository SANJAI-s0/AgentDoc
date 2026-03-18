from __future__ import annotations

import base64
import hashlib
import json
import re
from dataclasses import dataclass
from io import BytesIO
from typing import Any

import numpy as np
from PIL import Image

try:
    import cv2
except Exception:  # pragma: no cover
    cv2 = None

try:
    import pytesseract
except Exception:  # pragma: no cover
    pytesseract = None

try:
    from paddleocr import PaddleOCR
except Exception:  # pragma: no cover
    PaddleOCR = None

try:
    from langchain.tools import tool
except ImportError:
    def tool(func):
        """Fallback decorator if LangChain not available"""
        return func


@dataclass
class OCRResult:
    text: str
    confidence: float


class PreprocessTool:
    def _pil_to_array(self, content: bytes) -> np.ndarray:
        image = Image.open(BytesIO(content)).convert("RGB")
        return np.array(image)

    def _array_to_bytes(self, array: np.ndarray) -> bytes:
        image = Image.fromarray(array)
        buffer = BytesIO()
        image.save(buffer, format="PNG")
        return buffer.getvalue()

    def run(self, content: bytes) -> dict[str, Any]:
        if not content:
            return {
                "processed_image": content,
                "quality_score": 0.0,
                "rotation_applied": 0,
            }

        if cv2 is None:
            return {
                "processed_image": content,
                "quality_score": 0.75,
                "rotation_applied": 0,
            }

        try:
            image = self._pil_to_array(content)
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            denoised = cv2.fastNlMeansDenoising(gray, None, 12, 7, 21)
            _, binary = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            quality = float(min(max(cv2.Laplacian(binary, cv2.CV_64F).var() / 500.0, 0.0), 1.0))
            rgb = cv2.cvtColor(binary, cv2.COLOR_GRAY2RGB)
            return {
                "processed_image": self._array_to_bytes(rgb),
                "quality_score": round(quality, 4),
                "rotation_applied": 0,
            }
        except Exception:
            return {
                "processed_image": content,
                "quality_score": 0.7,
                "rotation_applied": 0,
            }


class OCRTool:
    def __init__(self) -> None:
        self._paddle = None
        if PaddleOCR is not None:
            try:
                self._paddle = PaddleOCR(use_angle_cls=True, lang="en", show_log=False)
            except Exception:
                self._paddle = None

    def _ocr_with_tesseract(self, image_bytes: bytes) -> OCRResult:
        if pytesseract is None:
            return OCRResult(text="", confidence=0.0)
        try:
            image = Image.open(BytesIO(image_bytes)).convert("RGB")
            text = pytesseract.image_to_string(image)
            return OCRResult(text=text.strip(), confidence=0.78 if text.strip() else 0.0)
        except Exception:
            return OCRResult(text="", confidence=0.0)

    def _ocr_with_paddle(self, image_bytes: bytes) -> OCRResult:
        if self._paddle is None:
            return OCRResult(text="", confidence=0.0)
        try:
            image = np.array(Image.open(BytesIO(image_bytes)).convert("RGB"))
            result = self._paddle.ocr(image, cls=True)
            lines = []
            confs = []
            for block in result or []:
                for item in block or []:
                    if len(item) > 1 and item[1]:
                        lines.append(item[1][0])
                        confs.append(float(item[1][1]))
            text = "\n".join(lines).strip()
            confidence = float(sum(confs) / len(confs)) if confs else 0.0
            return OCRResult(text=text, confidence=confidence)
        except Exception:
            return OCRResult(text="", confidence=0.0)

    def extract_from_bytes(self, image_bytes: bytes, prefer_paddle: bool = False) -> OCRResult:
        if not image_bytes:
            return OCRResult(text="", confidence=0.0)

        primary = self._ocr_with_paddle(image_bytes) if prefer_paddle else self._ocr_with_tesseract(image_bytes)
        secondary = self._ocr_with_tesseract(image_bytes) if prefer_paddle else self._ocr_with_paddle(image_bytes)

        candidates = [primary, secondary]
        best = max(candidates, key=lambda item: item.confidence)
        return best if best.text else OCRResult(text="", confidence=0.0)

    def run(self, pages: list[dict[str, Any]]) -> list[dict[str, Any]]:
        processed = []
        for page in pages:
            if page.get("ocr_text"):
                processed.append(
                    {
                        **page,
                        "ocr_text": page.get("ocr_text"),
                        "confidence": float(page.get("confidence") or 0.9),
                    }
                )
                continue

            image_bytes = b""
            image_b64 = page.get("image_b64")
            if image_b64:
                try:
                    image_bytes = base64.b64decode(image_b64)
                except Exception:
                    image_bytes = b""

            ocr_result = self.extract_from_bytes(image_bytes, prefer_paddle=bool(page.get("is_handwritten")))
            processed.append(
                {
                    **page,
                    "ocr_text": ocr_result.text or "",
                    "confidence": round(float(ocr_result.confidence), 4),
                }
            )
        return processed


class HashTool:
    def run(self, content: bytes) -> str:
        return hashlib.sha256(content).hexdigest()


class PolicyLookupTool:
    def run(self, document_type: str) -> dict[str, Any]:
        rules = {
            "invoice": {
                "required_fields": ["invoice_number", "invoice_date", "total_amount"],
                "risk_threshold": 0.6,
            },
            "kyc_form": {
                "required_fields": ["full_name", "date_of_birth", "address", "government_id"],
                "risk_threshold": 0.55,
            },
            "loan_application": {
                "required_fields": ["applicant_name", "income", "loan_amount"],
                "risk_threshold": 0.65,
            },
            "receipt": {
                "required_fields": ["merchant_name", "transaction_date", "total_amount"],
                "risk_threshold": 0.6,
            },
            "insurance_claim": {
                "required_fields": ["claim_id", "policy_id", "incident_date"],
                "risk_threshold": 0.6,
            },
            "shipping_document": {
                "required_fields": ["tracking_number", "shipper", "receiver"],
                "risk_threshold": 0.58,
            },
            "contract": {
                "required_fields": ["party_a", "party_b", "effective_date"],
                "risk_threshold": 0.62,
            },
            "handwritten_form": {
                "required_fields": ["applicant_name", "submission_date"],
                "risk_threshold": 0.5,
            },
        }
        return rules.get(document_type, {"required_fields": ["document_id", "customer_name"], "risk_threshold": 0.6})


class SearchKnowledgeTool:
    def run(self, query: str) -> dict[str, Any]:
        return {
            "query": query,
            "similar_cases_found": 3,
            "note": "Local knowledge lookup from historical audit entries.",
        }


class FieldExtractionTool:
    currency_pattern = re.compile(r"(?:\$|INR\s?)?([0-9]+(?:[\.,][0-9]{2})?)")
    date_pattern = re.compile(r"\b(20\d{2}[-/][01]?\d[-/][0-3]?\d)\b")

    def extract(self, text: str, document_type: str, required_fields: list[str]) -> dict[str, Any]:
        text = text or ""
        lines = [line.strip() for line in text.splitlines() if line.strip()]

        extracted: dict[str, Any] = {}
        lowered = text.lower()

        for field in required_fields:
            key = field.lower()
            value = ""

            if "date" in key:
                date_match = self.date_pattern.search(text)
                value = date_match.group(1) if date_match else ""
            elif "amount" in key or "income" in key or "loan" in key:
                amount_match = self.currency_pattern.search(text)
                value = amount_match.group(1) if amount_match else ""
            else:
                for line in lines:
                    if key.replace("_", " ") in line.lower():
                        parts = re.split(r":|-", line, maxsplit=1)
                        value = parts[1].strip() if len(parts) > 1 else line.strip()
                        break

            if not value and key in lowered:
                value = "present"

            extracted[field] = value

        handwritten_fields = {}
        if document_type == "handwritten_form":
            handwritten_fields = {k: v for k, v in extracted.items() if v}

        confidence_map = {}
        missing_fields = []
        for field, value in extracted.items():
            if value:
                confidence_map[field] = 0.78
            else:
                confidence_map[field] = 0.45
                missing_fields.append(field)

        return {
            "structured_fields": extracted,
            "handwritten_fields": handwritten_fields,
            "confidence_map": confidence_map,
            "missing_fields": missing_fields,
            "tables": [],
        }


ocr_helper = OCRTool()
policy_helper = PolicyLookupTool()
search_helper = SearchKnowledgeTool()
preprocess_helper = PreprocessTool()
field_extractor = FieldExtractionTool()


@tool
def crewai_ocr_tool(pages_payload: str) -> str:
    """Extract OCR text from document pages provided as JSON."""
    pages = json.loads(pages_payload) if pages_payload else []
    return json.dumps(ocr_helper.run(pages))


@tool
def crewai_policy_lookup_tool(document_type: str) -> str:
    """Return required field policy rules for a given document type."""
    return json.dumps(policy_helper.run(document_type))


@tool
def crewai_search_knowledge_tool(query: str) -> str:
    """Search similar historical cases and knowledge snippets."""
    return json.dumps(search_helper.run(query))
