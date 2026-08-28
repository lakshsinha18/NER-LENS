"""PostGIS query helpers with a demo-safe fallback.

The Docker database enables PostGIS. The demo's compact WKT columns make the
prototype portable to SQLite; production migrations should promote them to
geometry(Point, 4326) / geometry(Geometry, 4326) and use these SQL predicates.
"""
from sqlalchemy import text
from sqlalchemy.orm import Session


def nearby_features_postgis(db: Session, longitude: float, latitude: float, distance_m: int = 5000):
    sql = text("""
        SELECT name, type, importance
        FROM infrastructure
        WHERE ST_DWithin(
          ST_SetSRID(ST_GeomFromText(geometry), 4326)::geography,
          ST_SetSRID(ST_MakePoint(:longitude, :latitude), 4326)::geography,
          :distance_m
        )
    """)
    return db.execute(sql, {"longitude": longitude, "latitude": latitude, "distance_m": distance_m}).mappings().all()


def nearby_by_bounding_box(items, latitude: float, longitude: float, degrees: float = .06):
    """Fallback used by the SQLite demo database and unit tests."""
    return [item for item in items if abs(item.latitude - latitude) <= degrees and abs(item.longitude - longitude) <= degrees]
