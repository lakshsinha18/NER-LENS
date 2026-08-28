from datetime import datetime, timedelta
from sqlalchemy import func
from sqlalchemy.orm import Session
from ..auth import hash_password
from ..models import Alert, EmergencyTask, HazardReport, Infrastructure, Location, RiskZone, Road, SatelliteObservation, User, WeatherData
from .priority import priority_for

ZONES = [
    ("Aizawl Ridge", "Aizawl", "Mizoram", 23.727, 92.717, 87, 78, 38, 134),
    ("East Khasi Hills", "Shillong", "Meghalaya", 25.578, 91.893, 72, 71, 34, 104),
    ("Sikkim Corridor", "Gangtok", "Sikkim", 27.338, 88.606, 65, 63, 31, 89),
    ("Papum Pare Hills", "Itanagar", "Arunachal Pradesh", 27.103, 93.618, 58, 60, 29, 69),
    ("Dima Hasao", "Haflong", "Assam", 25.171, 93.017, 49, 55, 27, 58),
    ("Chandel Escarpment", "Chandel", "Manipur", 24.333, 94.052, 43, 50, 26, 47),
    ("Kohima South", "Kohima", "Nagaland", 25.658, 94.110, 37, 47, 22, 38),
    ("Jampui Hills", "North Tripura", "Tripura", 24.001, 92.273, 25, 42, 17, 27),
]


def level(score: float) -> str:
    return "CRITICAL" if score >= 81 else "HIGH" if score >= 61 else "MODERATE" if score >= 31 else "LOW"


def seed_demo_data(db: Session) -> None:
    if db.scalar(func.count(RiskZone.id)):
        return
    demo_users = [
        ("Demo Administrator", "admin@nerlens.demo", "ADMIN", "Aizawl"),
        ("Mizoram District Authority", "authority@nerlens.demo", "DISTRICT_AUTHORITY", "Aizawl"),
        ("Field Officer Demo", "field@nerlens.demo", "FIELD_OFFICER", "Shillong"),
        ("Citizen Demo", "citizen@nerlens.demo", "CITIZEN", "Gangtok"),
    ]
    for name, email, role, district in demo_users:
        db.add(User(name=name, email=email, role=role, district=district, language="en", password_hash=hash_password("Demo@123")))
    for i, (name, district, state, lat, lng, score, moisture, slope, rain) in enumerate(ZONES, 1):
        db.add(Location(id=i, name=name, district=district, state=state, latitude=lat, longitude=lng, geometry=f"POINT({lng} {lat})"))
        db.add(RiskZone(zone_name=name, district=district, state=state, latitude=lat, longitude=lng, geometry=f"POINT({lng} {lat})", risk_score=score, risk_level=level(score), probability=score / 100, rainfall_24h=rain, soil_moisture=moisture, slope=slope, forecast_rainfall=max(9, rain * .31)))
        db.add(WeatherData(location_id=i, rainfall_1h=max(1, rain * .09), rainfall_6h=rain * .31, rainfall_24h=rain, rainfall_72h=rain * 1.9, rainfall_7d=rain * 3.4, temperature=24 - (i % 4), forecast_rainfall=rain * .31))
        db.add(SatelliteObservation(location_id=i, change_score=round(score * .61, 1), deformation_score=round(score * .52, 1), landslide_indicator="elevated_change" if score > 60 else "stable", image_url=None))
    db.add_all([
        Road(road_name="NH-306 Aizawl Corridor", road_type="National Highway", latitude=23.735, longitude=92.729, geometry="LINESTRING(92.69 23.69, 92.75 23.76)", status="MONITORING", criticality=1.45),
        Road(road_name="Shillong Bypass", road_type="State Highway", latitude=25.588, longitude=91.882, geometry="LINESTRING(91.84 25.56, 91.92 25.61)", status="OPEN", criticality=1.18),
        Road(road_name="Gangtok–Rangpo Road", road_type="National Highway", latitude=27.315, longitude=88.598, geometry="LINESTRING(88.55 27.28, 88.64 27.35)", status="PARTIALLY_BLOCKED", criticality=1.39),
        Road(road_name="Haflong Hill Road", road_type="District Road", latitude=25.177, longitude=93.030, geometry="LINESTRING(92.99 25.15, 93.06 25.19)", status="OPEN", criticality=1.12),
    ])
    db.add_all([
        Infrastructure(name="Aizawl District Hospital", type="Hospital", importance=1.45, geometry="POINT(92.719 23.731)"),
        Infrastructure(name="Shillong Water Supply", type="Water utility", importance=1.30, geometry="POINT(91.897 25.580)"),
        Infrastructure(name="Rangpo Bridge", type="Bridge", importance=1.42, geometry="POINT(88.604 27.320)"),
        Infrastructure(name="Chandel School Cluster", type="School", importance=1.15, geometry="POINT(94.057 24.339)"),
    ])
    db.add_all([
        HazardReport(user_id=3, report_type="Slope movement", description="Fresh soil displacement observed beside the hill road. Demo report for workflow testing.", latitude=23.732, longitude=92.725, geometry="POINT(92.725 23.732)", ai_classification="possible_landslide", ai_confidence=.58, severity="HIGH", status="UNDER_REVIEW"),
        HazardReport(user_id=4, report_type="Blocked road", description="Small debris fall affecting one lane; demo report, not a verified incident.", latitude=27.318, longitude=88.601, geometry="POINT(88.601 27.318)", ai_classification="blocked_road", ai_confidence=.63, severity="MODERATE", status="VERIFIED"),
    ])
    db.add_all([
        Alert(alert_type="EARLY_WARNING", severity="CRITICAL", title="Critical landslide watch — Aizawl Ridge", message="DEMO / SIMULATED DATA: Avoid exposed slopes and follow district authority guidance. This is a prediction, not a confirmed event.", target_area="Aizawl"),
        Alert(alert_type="ROAD_MONITORING", severity="HIGH", title="Monitoring: Gangtok–Rangpo Road", message="DEMO / SIMULATED DATA: partial obstruction workflow active.", target_area="Gangtok"),
    ])
    for zone in ZONES[:4]:
        name, district, _, _, _, score, _, _, _ = zone
        calculation = priority_for(score, 1.28, 1.35, 1.3, 1.14)
        db.add(EmergencyTask(incident_id=None, priority=calculation["priority"], priority_score=calculation["priority_score"], assigned_team="NER Response Cell" if score >= 70 else None, status="ASSIGNED" if score >= 70 else "UNASSIGNED", explanation=f"{name}: {calculation['why']}"))
    db.commit()


def apply_simulation(db: Session, scenario: str) -> list[RiskZone]:
    factors = {"normal": .55, "heavy_rainfall": 1.15, "extreme_rainfall": 1.45, "critical_warning": 1.72}
    if scenario not in factors:
        raise ValueError("Unknown simulation scenario")
    factor = factors[scenario]
    zones = db.query(RiskZone).all()
    for index, zone in enumerate(zones):
        rain = min(260, zone.rainfall_24h * factor + (12 if scenario != "normal" else -15))
        moisture = min(96, max(25, zone.soil_moisture * (.92 + factor * .18)))
        score = min(98, max(8, round(zone.risk_score * factor + (8 if index < 2 and scenario in {"extreme_rainfall", "critical_warning"} else 0))))
        zone.rainfall_24h = round(rain, 1)
        zone.soil_moisture = round(moisture, 1)
        zone.forecast_rainfall = round(rain * .38, 1)
        zone.risk_score = score
        zone.probability = score / 100
        zone.risk_level = level(score)
    critical = [z for z in zones if z.risk_level == "CRITICAL"]
    if critical:
        target = critical[0]
        db.add(Alert(alert_type="SIMULATION", severity="CRITICAL", title=f"Simulation alert — {target.zone_name}", message="DEMO / SIMULATED DATA: Disaster simulation elevated risk. No real notification was sent.", target_area=target.district))
    db.commit()
    return zones


def reset_demo(db: Session) -> None:
    # Repeatable simulation reset without deleting user-created reports.
    for zone, baseline in zip(db.query(RiskZone).order_by(RiskZone.id).all(), ZONES):
        _, _, _, _, _, score, moisture, slope, rain = baseline
        zone.risk_score, zone.risk_level, zone.probability = score, level(score), score / 100
        zone.soil_moisture, zone.slope, zone.rainfall_24h, zone.forecast_rainfall = moisture, slope, rain, max(9, rain * .31)
    db.commit()
