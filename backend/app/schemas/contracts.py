from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)


class RegisterRequest(LoginRequest):
    name: str = Field(min_length=2, max_length=120)
    role: str = "CITIZEN"
    district: str | None = None
    language: str = "en"


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict


class RiskInput(BaseModel):
    rainfall_1h: float = Field(ge=0, le=1000)
    rainfall_6h: float = Field(ge=0, le=2000)
    rainfall_24h: float = Field(ge=0, le=3000)
    rainfall_72h: float = Field(ge=0, le=5000)
    rainfall_7d: float = Field(ge=0, le=10000)
    soil_moisture: float = Field(ge=0, le=100)
    slope: float = Field(ge=0, le=90)
    elevation: float = Field(ge=-500, le=10000)
    aspect: float = Field(ge=0, le=360)
    historical_landslide_count: int = Field(ge=0, le=10000)
    distance_to_road: float = Field(ge=0, le=1000)
    land_cover_risk: float = Field(ge=0, le=1)


class ReportCreate(BaseModel):
    report_type: str = Field(min_length=2, max_length=80)
    description: str = Field(min_length=5, max_length=2000)
    latitude: float = Field(ge=6, le=38)
    longitude: float = Field(ge=68, le=98)
    landmark: str | None = Field(default=None, max_length=160)
    image_url: str | None = None
    video_url: str | None = None


class RoadUpdate(BaseModel):
    status: str = Field(pattern="^(OPEN|MONITORING|PARTIALLY_BLOCKED|BLOCKED)$")


class SensorData(BaseModel):
    sensor_id: str = Field(min_length=2, max_length=80)
    latitude: float = Field(ge=6, le=38)
    longitude: float = Field(ge=68, le=98)
    soil_moisture: float = Field(ge=0, le=100)
    timestamp: datetime


class AlertCreate(BaseModel):
    alert_type: str
    severity: str
    title: str
    message: str
    target_area: str
    expires_at: datetime | None = None


class UserRoleUpdate(BaseModel):
    role: str = Field(pattern="^(ADMIN|DISTRICT_AUTHORITY|FIELD_OFFICER|CITIZEN)$")


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)
