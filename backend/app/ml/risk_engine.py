"""Explainable, deterministic baseline risk engine.

The weighting is intentionally transparent in demo mode.  A trained joblib model,
when available, is used as an additional input but never treated as certainty.
"""
from pathlib import Path
from typing import Any
import joblib
import numpy as np
import pandas as pd
from ..schemas import RiskInput

FEATURES = [
    "rainfall_1h", "rainfall_6h", "rainfall_24h", "rainfall_72h", "rainfall_7d",
    "soil_moisture", "slope", "elevation", "aspect", "historical_landslide_count",
    "distance_to_road", "land_cover_risk",
]


class RiskEngine:
    def __init__(self) -> None:
        self.model: Any | None = None
        candidates = [
            Path(__file__).resolve().parents[3] / "ml/models/landslide_model.pkl",
            Path("ml/models/landslide_model.pkl"),
        ]
        for path in candidates:
            if path.exists():
                try:
                    self.model = joblib.load(path)
                    break
                except Exception:
                    continue

    def predict(self, data: RiskInput | dict) -> dict:
        values = data.model_dump() if isinstance(data, RiskInput) else data
        rainfall_pressure = min(1.0, (values["rainfall_24h"] * .48 + values["rainfall_72h"] * .18 + values["rainfall_1h"] * .34) / 145)
        moisture_pressure = min(1.0, values["soil_moisture"] / 100)
        terrain_pressure = min(1.0, values["slope"] / 48)
        history_pressure = min(1.0, values["historical_landslide_count"] / 8)
        land_cover_pressure = float(values["land_cover_risk"])
        road_pressure = max(0.0, 1 - min(values["distance_to_road"], 10) / 10)
        rule_probability = (
            rainfall_pressure * .34 + moisture_pressure * .24 + terrain_pressure * .19 +
            history_pressure * .11 + land_cover_pressure * .08 + road_pressure * .04
        )
        model_probability = None
        if self.model is not None:
            try:
                row = pd.DataFrame([[values[name] for name in FEATURES]], columns=FEATURES)
                model_probability = float(self.model.predict_proba(row)[0][1])
            except Exception:
                model_probability = None
        probability = (rule_probability * .45 + model_probability * .55) if model_probability is not None else rule_probability
        safeguards: list[str] = []
        if values["rainfall_24h"] >= 110 and values["soil_moisture"] >= 78 and values["slope"] >= 30:
            probability = max(probability, .82)
            safeguards.append("Extreme rainfall, saturated soil and steep terrain safeguard applied")
        if values["rainfall_1h"] >= 45:
            probability = min(1.0, probability + .06)
            safeguards.append("Intense hourly rainfall safeguard applied")
        probability = round(float(np.clip(probability, 0, 1)), 3)
        score = round(probability * 100)
        level = "CRITICAL" if score >= 81 else "HIGH" if score >= 61 else "MODERATE" if score >= 31 else "LOW"
        reasons = []
        if values["rainfall_24h"] >= 70: reasons.append("Heavy 24-hour rainfall")
        if values["soil_moisture"] >= 68: reasons.append("High soil moisture")
        if values["slope"] >= 28: reasons.append("Steep terrain")
        if values["historical_landslide_count"] >= 3: reasons.append("Historical landslide activity")
        if values["rainfall_72h"] >= 150: reasons.append("Rainfall accumulation is increasing")
        if not reasons: reasons.append("Conditions currently remain below elevated-risk thresholds")
        confidence = .78 if model_probability is not None else .68
        return {
            "probability": probability, "risk_score": score, "risk_level": level,
            "confidence": confidence, "model": "Random Forest demo baseline" if model_probability is not None else "Explainable rule-based demo baseline",
            "prediction_notice": "This is a risk prediction, not a guaranteed landslide event.",
            "reasons": reasons, "safeguards": safeguards,
        }


risk_engine = RiskEngine()
