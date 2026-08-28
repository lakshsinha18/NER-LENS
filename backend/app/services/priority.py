def priority_for(risk_score: float, exposure_factor: float, infrastructure_criticality: float, connectivity_factor: float, response_difficulty: float) -> dict:
    raw = risk_score * exposure_factor * infrastructure_criticality * connectivity_factor * response_difficulty
    # Factors are normalized around 1.0. Preserve a bounded 0–100 operational score.
    score = round(min(100, max(0, raw / 1.35)))
    priority = "CRITICAL" if score >= 80 else "HIGH" if score >= 60 else "MEDIUM" if score >= 35 else "LOW"
    return {
        "priority_score": score, "priority": priority,
        "why": f"Risk {round(risk_score)} × exposure {exposure_factor:.2f} × infrastructure {infrastructure_criticality:.2f} × connectivity {connectivity_factor:.2f} × response difficulty {response_difficulty:.2f}",
    }
