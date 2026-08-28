from datetime import datetime
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from ..database import Base


class Timestamped:
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class User(Timestamped, Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(40), default="CITIZEN")
    district: Mapped[str | None] = mapped_column(String(120), nullable=True)
    language: Mapped[str] = mapped_column(String(10), default="en")


class Location(Base):
    __tablename__ = "locations"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(160))
    district: Mapped[str] = mapped_column(String(120))
    state: Mapped[str] = mapped_column(String(120))
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    geometry: Mapped[str | None] = mapped_column(Text, nullable=True)  # WKT; migrate to PostGIS Geometry in production.


class RiskZone(Base):
    __tablename__ = "risk_zones"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    zone_name: Mapped[str] = mapped_column(String(160))
    district: Mapped[str] = mapped_column(String(120))
    state: Mapped[str] = mapped_column(String(120))
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    geometry: Mapped[str | None] = mapped_column(Text, nullable=True)
    risk_score: Mapped[float] = mapped_column(Float, default=0)
    risk_level: Mapped[str] = mapped_column(String(20), default="LOW")
    probability: Mapped[float] = mapped_column(Float, default=0)
    rainfall_24h: Mapped[float] = mapped_column(Float, default=0)
    soil_moisture: Mapped[float] = mapped_column(Float, default=0)
    slope: Mapped[float] = mapped_column(Float, default=0)
    forecast_rainfall: Mapped[float] = mapped_column(Float, default=0)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class WeatherData(Base):
    __tablename__ = "weather_data"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    location_id: Mapped[int | None] = mapped_column(ForeignKey("locations.id"), nullable=True)
    rainfall_1h: Mapped[float] = mapped_column(Float, default=0)
    rainfall_6h: Mapped[float] = mapped_column(Float, default=0)
    rainfall_24h: Mapped[float] = mapped_column(Float, default=0)
    rainfall_72h: Mapped[float] = mapped_column(Float, default=0)
    rainfall_7d: Mapped[float] = mapped_column(Float, default=0)
    temperature: Mapped[float] = mapped_column(Float, default=0)
    forecast_rainfall: Mapped[float] = mapped_column(Float, default=0)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class SoilData(Base):
    __tablename__ = "soil_data"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    location_id: Mapped[int | None] = mapped_column(ForeignKey("locations.id"), nullable=True)
    soil_moisture: Mapped[float] = mapped_column(Float)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class TerrainData(Base):
    __tablename__ = "terrain_data"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    location_id: Mapped[int | None] = mapped_column(ForeignKey("locations.id"), nullable=True)
    elevation: Mapped[float] = mapped_column(Float)
    slope: Mapped[float] = mapped_column(Float)
    aspect: Mapped[float] = mapped_column(Float)
    geology: Mapped[str] = mapped_column(String(120), default="Mixed sedimentary")
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class HistoricalLandslide(Base):
    __tablename__ = "historical_landslides"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    location_id: Mapped[int | None] = mapped_column(ForeignKey("locations.id"), nullable=True)
    event_date: Mapped[datetime] = mapped_column(DateTime)
    severity: Mapped[str] = mapped_column(String(30))
    source: Mapped[str] = mapped_column(String(160), default="Demo data — unverified")
    geometry: Mapped[str | None] = mapped_column(Text, nullable=True)


class SatelliteObservation(Base):
    __tablename__ = "satellite_observations"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    location_id: Mapped[int | None] = mapped_column(ForeignKey("locations.id"), nullable=True)
    observation_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    change_score: Mapped[float] = mapped_column(Float)
    deformation_score: Mapped[float] = mapped_column(Float)
    landslide_indicator: Mapped[str] = mapped_column(String(80))
    image_url: Mapped[str | None] = mapped_column(String(255), nullable=True)


class HazardReport(Timestamped, Base):
    __tablename__ = "hazard_reports"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    report_type: Mapped[str] = mapped_column(String(80))
    description: Mapped[str] = mapped_column(Text)
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    geometry: Mapped[str | None] = mapped_column(Text, nullable=True)
    image_url: Mapped[str | None] = mapped_column(String(255), nullable=True)
    video_url: Mapped[str | None] = mapped_column(String(255), nullable=True)
    ai_classification: Mapped[str] = mapped_column(String(80), default="uncertain")
    ai_confidence: Mapped[float] = mapped_column(Float, default=0.5)
    severity: Mapped[str] = mapped_column(String(30), default="MODERATE")
    status: Mapped[str] = mapped_column(String(30), default="PENDING_REVIEW")


class Road(Base):
    __tablename__ = "roads"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    road_name: Mapped[str] = mapped_column(String(160))
    road_type: Mapped[str] = mapped_column(String(80))
    geometry: Mapped[str | None] = mapped_column(Text, nullable=True)
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    status: Mapped[str] = mapped_column(String(30), default="OPEN")
    criticality: Mapped[float] = mapped_column(Float, default=1)
    last_updated: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Infrastructure(Base):
    __tablename__ = "infrastructure"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(160))
    type: Mapped[str] = mapped_column(String(80))
    importance: Mapped[float] = mapped_column(Float)
    geometry: Mapped[str | None] = mapped_column(Text, nullable=True)


class Alert(Timestamped, Base):
    __tablename__ = "alerts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    alert_type: Mapped[str] = mapped_column(String(80))
    severity: Mapped[str] = mapped_column(String(30))
    title: Mapped[str] = mapped_column(String(200))
    message: Mapped[str] = mapped_column(Text)
    target_area: Mapped[str] = mapped_column(String(160))
    expires_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="ACTIVE")


class EmergencyTask(Timestamped, Base):
    __tablename__ = "emergency_tasks"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    incident_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    priority: Mapped[str] = mapped_column(String(30))
    priority_score: Mapped[float] = mapped_column(Float)
    assigned_team: Mapped[str | None] = mapped_column(String(120), nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="UNASSIGNED")
    explanation: Mapped[str] = mapped_column(Text, default="")


class SensorReading(Base):
    __tablename__ = "sensor_readings"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    sensor_id: Mapped[str] = mapped_column(String(80), index=True)
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    soil_moisture: Mapped[float] = mapped_column(Float)
    timestamp: Mapped[datetime] = mapped_column(DateTime)
