# NER-LENS

**North Eastern Region Landslide Early Warning & Network Safety Platform**

NER-LENS is a runnable Smart India Hackathon-style prototype for combining rainfall, soil moisture, terrain, historical activity, satellite change signals, citizen reports, road status, and emergency-impact factors into an explainable landslide-risk workflow.

> **Important:** The included locations, weather, satellite observations, historical activity, alerts, and model-training records are deterministic **DEMO / SIMULATED DATA**. They are not verified disaster records, live advisories, or a guarantee of any event.

## What is included

- Map-first React/Vite/TypeScript dashboard with Leaflet risk zones, road markers, drill-down detail panels, responsive reporting, alerts, priorities, weather, satellite, sensors, and model-monitoring views.
- FastAPI API with Swagger docs at `/docs`, Pydantic validation, password hashing, JWT access tokens, role checks, CORS configuration, WebSocket dashboard events, upload validation, and structured logging.
- SQLAlchemy domain model for users, locations, zones, weather/soil/terrain, historical observations, satellite observations, reports, roads, infrastructure, alerts, tasks and sensor readings.
- Docker PostGIS database. The demo persists WKT geometry so it can also run in SQLite without setup; [`backend/app/gis/spatial.py`](backend/app/gis/spatial.py) contains the PostGIS `ST_DWithin` query path for production geometry migrations.
- Explainable risk engine, rule safeguards, emergency-priority calculation, deterministic weather provider, image-triage contract, and satellite-provider architecture.
- Offline report queue using IndexedDB. Offline reports never claim to be synced; they are sent only after an explicit or automatic online sync.
- Four controllable simulation scenarios: `normal`, `heavy_rainfall`, `extreme_rainfall`, and `critical_warning`.

## Architecture

```text
Weather / sensors / satellite / reports / terrain
              ↓
       validation + persistence
              ↓
 explainable ML + rule risk engine
              ↓
 GIS map → impact / priority → alerts → live dashboard
```

The frontend only renders risk data received from the API. It does not contain hard-coded zone risks.

## Quick demo with Docker

1. Copy the environment template and replace the default secrets for any non-demo environment:

   ```bash
   cp .env.example .env
   ```

2. Launch the complete stack:

   ```bash
   docker compose up --build
   ```

3. Open `http://localhost:8080`. The API is at `http://localhost:8000`, including interactive docs at `http://localhost:8000/docs`.

Docker starts `frontend`, `backend`, and a PostGIS-enabled `postgres` service, then seeds the demo records on backend startup. No paid external API is needed.

## Local development

### Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Without `DATABASE_URL`, the local backend creates `backend/ner_lens_demo.db`. To use PostGIS locally, use the `DATABASE_URL` example from `.env.example`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Vite proxies `/api` and `/ws` to the local FastAPI service. Open `http://localhost:5173`.

## Demo credentials

All seeded accounts use the password `Demo@123`. These accounts are for demo use only:

| Role | Email |
| --- | --- |
| Administrator | `admin@nerlens.demo` |
| District authority | `authority@nerlens.demo` |
| Field officer | `field@nerlens.demo` |
| Citizen | `citizen@nerlens.demo` |

Sign in as the administrator to run a disaster simulation. Field officers, district authorities, and administrators can update road status. A `BLOCKED` critical road creates a task and an in-app demo alert.

## ML baseline

The model contract uses:

```text
rainfall_1h, rainfall_6h, rainfall_24h, rainfall_72h, rainfall_7d,
soil_moisture, slope, elevation, aspect, historical_landslide_count,
distance_to_road, land_cover_risk
```

Train the reproducible Random Forest demo baseline:

```bash
python scripts/train_model.py
```

It trains and compares a Random Forest baseline with the XGBoost main model when XGBoost's native runtime is available, selecting the better ROC-AUC model and writing `ml/models/landslide_model.pkl` plus `metrics.json`. On hosts without that runtime (such as a local macOS environment without OpenMP), it clearly falls back to the Random Forest baseline. The generator labels its data as synthetic training data. The runtime continues with a transparent rule baseline if the model file is absent.

## Demo data and seed scripts

```bash
python scripts/seed_database.py
python scripts/generate_demo_data.py
```

Seed data covers Assam, Arunachal Pradesh, Meghalaya, Manipur, Mizoram, Nagaland, Sikkim, and Tripura. Its purpose is a coherent live demonstration, not historical validation.

## API surface

| Area | Endpoints |
| --- | --- |
| Authentication | `POST /api/auth/register`, `POST /api/auth/login`, `GET /api/auth/me` |
| Risk | `GET /api/risk/zones`, `GET /api/risk/zones/{id}`, `POST /api/risk/predict` |
| Weather | `GET /api/weather/current`, `GET /api/weather/forecast` |
| Operations | `GET/PATCH /api/roads`, `GET/POST /api/reports`, `POST /api/reports/upload`, `GET/POST /api/alerts` |
| Dashboard | `GET /api/dashboard/stats`, `GET /api/dashboard/priorities`, `WS /ws/dashboard` |
| Integrations | `POST /api/sensors/data`, `GET /api/satellite/observations` |
| Simulation | `POST /api/simulation/start?scenario=critical_warning`, `POST /api/simulation/stop` |

Swagger provides the current authoritative contract. Sensitive endpoints use a bearer token from the demo login response.

## Testing

```bash
# after installing backend requirements from the repository root
PYTHONPATH=backend pytest -q tests

cd frontend && npm run build
```

The test suite covers risk-score bounds/explanation, priority calculation, basic API startup/seed behaviour, and frontend risk-level semantics. Add route/component integration tests with a disposable PostGIS database before operational deployment.

## Security and deployment notes

- Do not keep the example JWT secret or demo passwords in a deployed environment.
- External weather, SMS, email, and satellite credentials belong only in `.env` / deployment secrets, never browser code.
- Media upload validation allows JPG, PNG, WebP, MP4 and WebM up to `MAX_UPLOAD_MB`; production should use virus scanning and object storage.
- Rate limiting is left for the deployment edge/API gateway. Add it before exposing public report intake.
- Upgrade WKT demo columns to SRID 4326 PostGIS geometries and use verified spatial data before a real-world launch.

## Localization and offline operation

The user model stores a language preference and frontend localization is structured for English and Hindi first. Provider/template expansion for Assamese, Bengali, Mizo, Khasi, Manipuri, Nepali and Tripuri is intentionally separated from risk calculation. The report page uses IndexedDB to retain a basic report queue in low-connectivity mode; media is not falsely marked synced while offline.

## Future improvements

1. Ingest verified IMD/weather, sensor, inventory and satellite feeds through the provider adapters.
2. Train/calibrate and independently evaluate models on verified landslide labels, including an XGBoost comparison.
3. Apply Alembic migrations to native PostGIS geometry columns and run authoritative impact queries.
4. Add object storage, malware scanning, delivery providers, audit trails, multilingual templates and public rate limiting.
5. Add role-specific report/task workflows, notification acknowledgements and production observability.
