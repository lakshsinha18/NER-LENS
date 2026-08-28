from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any


class WeatherProvider(ABC):
    @abstractmethod
    def get_current_weather(self) -> dict[str, Any]: ...
    @abstractmethod
    def get_forecast(self) -> list[dict[str, Any]]: ...
    @abstractmethod
    def get_rainfall(self) -> dict[str, float]: ...


class MockWeatherProvider(WeatherProvider):
    """Deterministic demo provider; replace with an API-backed provider via .env."""
    def get_current_weather(self) -> dict[str, Any]:
        return {"mode": "DEMO / SIMULATED DATA", "location": "Northeast India", "temperature": 24.6, "condition": "Overcast", "observed_at": datetime.now(timezone.utc).isoformat()}

    def get_forecast(self) -> list[dict[str, Any]]:
        return [
            {"horizon": "Now", "rainfall_mm": 7, "condition": "Overcast"},
            {"horizon": "+6h", "rainfall_mm": 21, "condition": "Rain showers"},
            {"horizon": "+12h", "rainfall_mm": 33, "condition": "Heavy rain"},
            {"horizon": "+24h", "rainfall_mm": 28, "condition": "Rain showers"},
            {"horizon": "+48h", "rainfall_mm": 16, "condition": "Cloudy"},
        ]

    def get_rainfall(self) -> dict[str, float]:
        return {"rainfall_1h": 7, "rainfall_6h": 24, "rainfall_24h": 81, "rainfall_72h": 162, "rainfall_7d": 294}


weather_provider: WeatherProvider = MockWeatherProvider()
