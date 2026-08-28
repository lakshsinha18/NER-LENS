"""Write a transparent, small GeoJSON export for map demonstrations."""
import json
from pathlib import Path

ZONES = [
    ("Aizawl Ridge", 92.717, 23.727, "CRITICAL", 87), ("East Khasi Hills", 91.893, 25.578, "HIGH", 72),
    ("Sikkim Corridor", 88.606, 27.338, "HIGH", 65), ("Papum Pare Hills", 93.618, 27.103, "MODERATE", 58),
]
features = [{"type": "Feature", "properties": {"zone_name": n, "risk_level": l, "risk_score": s, "data_status": "DEMO / SIMULATED DATA"}, "geometry": {"type": "Point", "coordinates": [lng, lat]}} for n, lng, lat, l, s in ZONES]
path = Path(__file__).resolve().parents[1] / "data/geojson/demo_risk_zones.geojson"
path.write_text(json.dumps({"type": "FeatureCollection", "metadata": {"notice": "Demo data; not verified disaster records."}, "features": features}, indent=2))
print(path)
