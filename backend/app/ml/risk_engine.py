"""Explainable, deterministic baseline risk engine for the demo deployment.

The weighting is intentionally transparent and uses no bundled model artefacts.
This keeps the hosted demonstration small enough for a serverless function while
preserving the same clearly labelled, non-operational risk estimate.
"""
from ..schemas import RiskInput


class RiskEngine:
    def predict(self, data: RiskInput | dict) -> dict:
        values = data.model_dump() if isinstance(data, RiskInput) else data
        rainfall_pressure = min(1.0, (values["rainfall_24h"] * .48 + values["rainfall_72h"] * .18 + values["rainfall_1h"] * .34) / 145)
        moisture_pressure = min(1.0, values["soil_moisture"] / 100)
        terrain_pressure = min(1.0, values["slope"] / 48)
        history_pressure = min(1.0, values["historical_landslide_count"] / 8)
        land_cover_pressure = float(values["land_cover_risk"])
        road_pressure = max(0.0, 1 - min(values["distance_to_road"], 10) / 10)
        probability = (
            rainfall_pressure * .34 + moisture_pressure * .24 + terrain_pressure * .19 +
            history_pressure * .11 + land_cover_pressure * .08 + road_pressure * .04
        )
        safeguards: list[str] = []
        if values["rainfall_24h"] >= 110 and values["soil_moisture"] >= 78 and values["slope"] >= 30:
            probability = max(probability, .82)
            safeguards.append("Extreme rainfall, saturated soil and steep terrain safeguard applied")
        if values["rainfall_1h"] >= 45:
            probability = min(1.0, probability + .06)
            safeguards.append("Intense hourly rainfall safeguard applied")
        probability = round(min(1.0, max(0.0, probability)), 3)
        score = round(probability * 100)
        level = "CRITICAL" if score >= 81 else "HIGH" if score >= 61 else "MODERATE" if score >= 31 else "LOW"
        reasons = []
        if values["rainfall_24h"] >= 70: reasons.append("Heavy 24-hour rainfall")
        if values["soil_moisture"] >= 68: reasons.append("High soil moisture")
        if values["slope"] >= 28: reasons.append("Steep terrain")
        if values["historical_landslide_count"] >= 3: reasons.append("Historical landslide activity")
        if values["rainfall_72h"] >= 150: reasons.append("Rainfall accumulation is increasing")
        if not reasons: reasons.append("Conditions currently remain below elevated-risk thresholds")
        return {
            "probability": probability, "risk_score": score, "risk_level": level,
            "confidence": .68, "model": "Explainable rule-based demo baseline",
            "prediction_notice": "This is a risk prediction, not a guaranteed landslide event.",
            "reasons": reasons, "safeguards": safeguards,
        }


risk_engine = RiskEngine()
