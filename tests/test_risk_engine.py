from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))
from app.ml.risk_engine import risk_engine


def test_risk_output_is_bounded_and_explained():
    result = risk_engine.predict({"rainfall_1h": 52, "rainfall_6h": 130, "rainfall_24h": 184, "rainfall_72h": 330, "rainfall_7d": 620, "soil_moisture": 91, "slope": 38, "elevation": 1200, "aspect": 125, "historical_landslide_count": 6, "distance_to_road": 1, "land_cover_risk": .9})
    assert 0 <= result["probability"] <= 1
    assert 0 <= result["risk_score"] <= 100
    assert result["risk_level"] == "CRITICAL"
    assert result["reasons"]
