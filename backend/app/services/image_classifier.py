from pathlib import Path


def classify_report_image(filename: str | None) -> dict:
    """Safe prototype classifier contract; requires human verification in all cases."""
    suffix = Path(filename or "").suffix.lower()
    if suffix not in {".jpg", ".jpeg", ".png", ".webp"}:
        return {"classification": "uncertain", "confidence": 0.0, "human_verification_required": True}
    # A lightweight model can be registered here without changing the API contract.
    return {"classification": "possible_landslide", "confidence": 0.58, "human_verification_required": True, "notice": "Prototype image triage only; it is not scientifically definitive."}
