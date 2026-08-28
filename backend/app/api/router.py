from datetime import datetime, timedelta
import logging
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy import func
from sqlalchemy.orm import Session
from ..auth import create_access_token, get_current_user, hash_password, require_roles, verify_password
from ..database import get_db
from ..ml.risk_engine import risk_engine
from ..models import Alert, EmergencyTask, HazardReport, RiskZone, Road, SatelliteObservation, SensorReading, User
from ..schemas import AlertCreate, LoginRequest, RegisterRequest, ReportCreate, RiskInput, RoadUpdate, SensorData, UserRoleUpdate
from ..services.demo_data import apply_simulation, reset_demo
from ..services.image_classifier import classify_report_image
from ..services.priority import priority_for
from ..services.realtime import manager
from ..services.weather import weather_provider
from ..config import get_settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api")
settings = get_settings()


def as_zone(zone: RiskZone) -> dict:
    return {
        "id": zone.id, "zone_name": zone.zone_name, "district": zone.district, "state": zone.state,
        "latitude": zone.latitude, "longitude": zone.longitude, "risk_score": round(zone.risk_score),
        "risk_level": zone.risk_level, "probability": zone.probability, "rainfall_24h": zone.rainfall_24h,
        "soil_moisture": zone.soil_moisture, "slope": zone.slope, "forecast_rainfall": zone.forecast_rainfall,
        "updated_at": zone.updated_at.isoformat(), "is_demo": True,
        "explainability": {"reasons": zone_reasons(zone), "notice": "Predictions indicate relative risk, not a guaranteed event."},
    }


def zone_reasons(zone: RiskZone) -> list[str]:
    reasons = []
    if zone.rainfall_24h >= 70: reasons.append("Heavy 24-hour rainfall")
    if zone.soil_moisture >= 68: reasons.append("High soil moisture")
    if zone.slope >= 28: reasons.append("Steep terrain")
    if zone.risk_score >= 61: reasons.append("Accumulated terrain and rainfall risk")
    return reasons or ["Conditions are below elevated-risk thresholds"]


def as_road(road: Road) -> dict:
    return {"id": road.id, "road_name": road.road_name, "road_type": road.road_type, "status": road.status, "criticality": road.criticality, "latitude": road.latitude, "longitude": road.longitude, "last_updated": road.last_updated.isoformat(), "is_demo": True}


def as_report(report: HazardReport) -> dict:
    return {"id": report.id, "report_type": report.report_type, "description": report.description, "latitude": report.latitude, "longitude": report.longitude, "image_url": report.image_url, "video_url": report.video_url, "ai_classification": report.ai_classification, "ai_confidence": report.ai_confidence, "human_verification_required": True, "severity": report.severity, "status": report.status, "created_at": report.created_at.isoformat(), "is_demo": True}


@router.post("/auth/register", status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == payload.email.lower()).first():
        raise HTTPException(409, "An account with this email already exists")
    permitted_roles = {"CITIZEN", "FIELD_OFFICER", "DISTRICT_AUTHORITY", "ADMIN"}
    role = payload.role if payload.role in permitted_roles else "CITIZEN"
    user = User(name=payload.name, email=payload.email.lower(), password_hash=hash_password(payload.password), role=role, district=payload.district, language=payload.language)
    db.add(user); db.commit(); db.refresh(user)
    return {"access_token": create_access_token(user), "token_type": "bearer", "user": {"id": user.id, "name": user.name, "role": user.role, "language": user.language}}


@router.post("/auth/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email.lower()).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return {"access_token": create_access_token(user), "token_type": "bearer", "user": {"id": user.id, "name": user.name, "role": user.role, "district": user.district, "language": user.language}}


@router.get("/auth/me")
def current_me(user: User = Depends(get_current_user)):
    return {"id": user.id, "name": user.name, "email": user.email, "role": user.role, "district": user.district, "language": user.language}


@router.get("/users")
def users(db: Session = Depends(get_db), _: User = Depends(require_roles("ADMIN"))):
    return {"users": [{"id": u.id, "name": u.name, "email": u.email, "role": u.role, "district": u.district, "language": u.language, "created_at": u.created_at.isoformat()} for u in db.query(User).order_by(User.id).all()]}


@router.patch("/users/{user_id}")
async def update_user_role(user_id: int, payload: UserRoleUpdate, db: Session = Depends(get_db), _: User = Depends(require_roles("ADMIN"))):
    account = db.get(User, user_id)
    if not account:
        raise HTTPException(404, "User not found")
    account.role = payload.role
    db.commit(); db.refresh(account)
    result = {"id": account.id, "name": account.name, "email": account.email, "role": account.role, "district": account.district}
    await manager.broadcast("user_updated", result)
    return result


@router.get("/risk/zones")
def risk_zones(db: Session = Depends(get_db)):
    return {"mode": "DEMO / SIMULATED DATA", "zones": [as_zone(item) for item in db.query(RiskZone).order_by(RiskZone.risk_score.desc()).all()]}


@router.get("/risk/zones/{zone_id}")
def risk_zone(zone_id: int, db: Session = Depends(get_db)):
    zone = db.get(RiskZone, zone_id)
    if not zone: raise HTTPException(404, "Risk zone not found")
    nearby_roads = [as_road(r) for r in db.query(Road).all() if abs(r.latitude-zone.latitude) < .15 and abs(r.longitude-zone.longitude) < .15]
    return {**as_zone(zone), "nearby_villages": [f"{zone.district} demo community", f"{zone.zone_name} cluster"], "nearby_roads": nearby_roads, "critical_infrastructure": ["Demo hospital / school records available"], "recommended_action": "Activate monitoring and prepare district response coordination." if zone.risk_score >= 61 else "Maintain routine monitoring."}


@router.post("/risk/predict")
def predict(payload: RiskInput):
    result = risk_engine.predict(payload)
    logger.info("risk_prediction score=%s level=%s", result["risk_score"], result["risk_level"])
    return result


@router.get("/weather/current")
def weather_current():
    return weather_provider.get_current_weather()


@router.get("/weather/forecast")
def weather_forecast():
    return {"mode": "DEMO / SIMULATED DATA", "forecast": weather_provider.get_forecast()}


@router.get("/roads")
def roads(db: Session = Depends(get_db)):
    return {"mode": "DEMO / SIMULATED DATA", "roads": [as_road(road) for road in db.query(Road).all()]}


@router.patch("/roads/{road_id}")
async def update_road(road_id: int, payload: RoadUpdate, db: Session = Depends(get_db), user: User = Depends(require_roles("ADMIN", "DISTRICT_AUTHORITY", "FIELD_OFFICER"))):
    road = db.get(Road, road_id)
    if not road: raise HTTPException(404, "Road not found")
    road.status, road.last_updated = payload.status, datetime.utcnow()
    if payload.status == "BLOCKED" and road.criticality >= 1.3:
        calculation = priority_for(80, 1.25, road.criticality, 1.45, 1.2)
        db.add(EmergencyTask(priority=calculation["priority"], priority_score=calculation["priority_score"], assigned_team=None, status="UNASSIGNED", explanation=f"{road.road_name} blocked. {calculation['why']}"))
        db.add(Alert(alert_type="ROAD_BLOCKAGE", severity="HIGH", title=f"Critical road blocked: {road.road_name}", message="Demo notification created; no external SMS or email was sent.", target_area="Affected road corridor"))
    db.commit(); db.refresh(road)
    data = as_road(road)
    await manager.broadcast("road_updated", data)
    return data


@router.get("/reports")
def reports(db: Session = Depends(get_db)):
    return {"mode": "DEMO / SIMULATED DATA", "reports": [as_report(r) for r in db.query(HazardReport).order_by(HazardReport.created_at.desc()).all()]}


@router.post("/reports", status_code=status.HTTP_201_CREATED)
async def create_report(payload: ReportCreate, db: Session = Depends(get_db), user: User | None = Depends(lambda: None)):
    # Anonymous citizen reporting is permitted; a production deployment can require a verified token.
    ai = classify_report_image(payload.image_url)
    severity = "HIGH" if payload.report_type.lower() in {"landslide", "blocked road", "slope movement"} else "MODERATE"
    report = HazardReport(user_id=user.id if user else None, report_type=payload.report_type, description=payload.description, latitude=payload.latitude, longitude=payload.longitude, geometry=f"POINT({payload.longitude} {payload.latitude})", image_url=payload.image_url, video_url=payload.video_url, ai_classification=ai["classification"], ai_confidence=ai["confidence"], severity=severity, status="PENDING_REVIEW")
    db.add(report); db.commit(); db.refresh(report)
    result = as_report(report)
    await manager.broadcast("report_created", result)
    logger.info("hazard_report_created id=%s", report.id)
    return {**result, "workflow": ["Stored report", "AI triage completed", "Human verification required", "Authority dashboard notified"]}


@router.post("/reports/upload", status_code=status.HTTP_201_CREATED)
async def upload_report_media(file: UploadFile = File(...)):
    """Local/object-storage adapter for small report photos and videos."""
    allowed = {"image/jpeg", "image/png", "image/webp", "video/mp4", "video/webm"}
    if file.content_type not in allowed:
        raise HTTPException(415, "Use JPG, PNG, WebP, MP4, or WebM media")
    content = await file.read()
    if len(content) > settings.max_upload_mb * 1024 * 1024:
        raise HTTPException(413, f"Media exceeds the {settings.max_upload_mb} MB limit")
    safe_name = f"{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}_{(file.filename or 'report_media').replace('/', '_')}"
    (settings.upload_path / safe_name).write_bytes(content)
    classification = classify_report_image(file.filename) if file.content_type.startswith("image/") else {"classification": "uncertain", "confidence": 0.0, "human_verification_required": True}
    return {"url": f"/uploads/{safe_name}", "content_type": file.content_type, "ai_triage": classification, "human_verification_required": True}


@router.get("/reports/{report_id}")
def report_detail(report_id: int, db: Session = Depends(get_db)):
    report = db.get(HazardReport, report_id)
    if not report: raise HTTPException(404, "Report not found")
    return as_report(report)


@router.get("/alerts")
def alerts(db: Session = Depends(get_db)):
    items = db.query(Alert).filter(Alert.status == "ACTIVE").order_by(Alert.created_at.desc()).all()
    return {"mode": "DEMO / SIMULATED DATA", "alerts": [{"id": a.id, "alert_type": a.alert_type, "severity": a.severity, "title": a.title, "message": a.message, "target_area": a.target_area, "created_at": a.created_at.isoformat(), "status": a.status} for a in items]}


@router.post("/alerts", status_code=status.HTTP_201_CREATED)
async def create_alert(payload: AlertCreate, db: Session = Depends(get_db), user: User = Depends(require_roles("ADMIN", "DISTRICT_AUTHORITY"))):
    alert = Alert(**payload.model_dump(), status="ACTIVE")
    db.add(alert); db.commit(); db.refresh(alert)
    data = {"id": alert.id, **payload.model_dump(), "status": alert.status, "created_at": alert.created_at.isoformat()}
    await manager.broadcast("alert_created", data)
    return {**data, "delivery": "Demo notification sent — no external SMS or email provider configured."}


@router.get("/dashboard/stats")
def dashboard_stats(db: Session = Depends(get_db)):
    zones = db.query(RiskZone).all()
    roads = db.query(Road).all()
    return {"mode": "DEMO / SIMULATED DATA", "stats": {"critical_zones": sum(z.risk_level == "CRITICAL" for z in zones), "high_risk_zones": sum(z.risk_level == "HIGH" for z in zones), "open_alerts": db.query(Alert).filter(Alert.status == "ACTIVE").count(), "roads_at_risk": sum(r.status != "OPEN" for r in roads), "active_field_reports": db.query(HazardReport).filter(HazardReport.status != "RESOLVED").count()}, "trend": [{"hour": label, "risk": score} for label, score in [("-24h", 43), ("-18h", 48), ("-12h", 55), ("-6h", 62), ("Now", round(sum(z.risk_score for z in zones) / max(1, len(zones))))]]}


@router.get("/dashboard/priorities")
def dashboard_priorities(db: Session = Depends(get_db)):
    tasks = db.query(EmergencyTask).order_by(EmergencyTask.priority_score.desc()).all()
    return {"mode": "DEMO / SIMULATED DATA", "priorities": [{"id": item.id, "priority": item.priority, "priority_score": item.priority_score, "assigned_team": item.assigned_team, "status": item.status, "explanation": item.explanation} for item in tasks]}


@router.post("/sensors/data", status_code=status.HTTP_201_CREATED)
async def sensor_data(payload: SensorData, db: Session = Depends(get_db)):
    reading = SensorReading(**payload.model_dump())
    db.add(reading)
    closest = min(db.query(RiskZone).all(), key=lambda z: (z.latitude-payload.latitude)**2 + (z.longitude-payload.longitude)**2, default=None)
    if closest:
        closest.soil_moisture = payload.soil_moisture
        # Recalculate zone using its current realistic feature context.
        result = risk_engine.predict({"rainfall_1h": closest.rainfall_24h*.1, "rainfall_6h": closest.rainfall_24h*.3, "rainfall_24h": closest.rainfall_24h, "rainfall_72h": closest.rainfall_24h*1.8, "rainfall_7d": closest.rainfall_24h*3.2, "soil_moisture": closest.soil_moisture, "slope": closest.slope, "elevation": 850, "aspect": 160, "historical_landslide_count": 4, "distance_to_road": 1.5, "land_cover_risk": .7})
        closest.risk_score, closest.risk_level, closest.probability = result["risk_score"], result["risk_level"], result["probability"]
    db.commit()
    event = {"sensor_id": payload.sensor_id, "nearest_zone": closest.zone_name if closest else None, "soil_moisture": payload.soil_moisture}
    await manager.broadcast("sensor_updated", event)
    return {"accepted": True, "mode": "DEMO / SIMULATED DATA", **event}


@router.get("/satellite/observations")
def satellite(db: Session = Depends(get_db)):
    observations = db.query(SatelliteObservation).order_by(SatelliteObservation.observation_date.desc()).all()
    return {"mode": "Satellite analysis: Demo mode", "architecture": ["satellite image", "preprocessing", "image comparison", "change detection", "risk engine"], "observations": [{"id": o.id, "location_id": o.location_id, "observation_date": o.observation_date.isoformat(), "change_score": o.change_score, "deformation_score": o.deformation_score, "landslide_indicator": o.landslide_indicator, "image_url": o.image_url} for o in observations]}


@router.post("/simulation/start")
async def start_simulation(scenario: str = "extreme_rainfall", db: Session = Depends(get_db), user: User = Depends(require_roles("ADMIN"))):
    try: zones = apply_simulation(db, scenario)
    except ValueError as exc: raise HTTPException(422, str(exc))
    payload = {"scenario": scenario, "message": "DEMO / SIMULATED DATA: disaster simulation running", "zones": [as_zone(z) for z in zones]}
    await manager.broadcast("simulation_updated", payload)
    return payload


@router.post("/simulation/stop")
async def stop_simulation(db: Session = Depends(get_db), user: User = Depends(require_roles("ADMIN"))):
    reset_demo(db)
    payload = {"message": "Simulation stopped; baseline demo conditions restored."}
    await manager.broadcast("simulation_stopped", payload)
    return payload
