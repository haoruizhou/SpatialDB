import os
import time
import logging
import requests
import psycopg2
from psycopg2.extras import RealDictCursor
from coord_convert.transform import wgs2gcj, gcj2wgs

# ── CONFIG & LOGGING ────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

TESTING_FLAG = False
DATABASE_URL = os.getenv("DATABASE_URL")
AMAP_KEY     = os.getenv("AMAP_KEY")
try:
    SLEEP_SEC = int(os.getenv("WORKER_INTERVAL", "10"))
except ValueError:
    logger.warning("Invalid WORKER_INTERVAL; defaulting to 10 seconds")
    SLEEP_SEC = 10

GEOCODE_URL = "https://restapi.amap.com/v3/geocode/geo"
MAX_ATTEMPTS = 3

if not DATABASE_URL or not AMAP_KEY:
    logger.critical("DATABASE_URL and AMAP_KEY must be set in environment")
    raise SystemExit(1)

# ── SCHEMA ENSURANCE ────────────────────────────────────────────────────────────
def ensure_tracking_columns(conn):
    """Create geocode_attempts and geocode_failed if they don't exist."""
    with conn.cursor() as cur:
        cur.execute("""
            ALTER TABLE project_data
              ADD COLUMN IF NOT EXISTS geocode_attempts INTEGER NOT NULL DEFAULT 0,
              ADD COLUMN IF NOT EXISTS geocode_failed   BOOLEAN NOT NULL DEFAULT FALSE;
        """)
    conn.commit()
    logger.info("Ensured tracking columns exist on project_data.")

# ── GEOCODE CALL ────────────────────────────────────────────────────────────────
def geocode(query: str):
    params = {"key": AMAP_KEY, "address": query, "output": "json"}
    try:
        resp = requests.get(GEOCODE_URL, params=params, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        if data.get("status") == "1" and data.get("geocodes"):
            lon_gcj, lat_gcj = map(float, data["geocodes"][0]["location"].split(","))
            return lon_gcj, lat_gcj
        logger.warning("No geocode result for '%s': %s", query, data)
    except requests.RequestException as e:
        logger.error("HTTP error during geocode(%s): %s", query, e)
    except (ValueError, KeyError) as e:
        logger.error("Error parsing geocode response for '%s': %s", query, e)
    return None, None

# ── WORKER ─────────────────────────────────────────────────────────────────────
def update_project_data(conn):
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        # select rows that haven't exceeded attempt limit or been marked failed
        cur.execute("""
            SELECT id, district, address, name, geocode_attempts
              FROM project_data
             WHERE lon_gcj02 IS NULL
               AND geocode_failed   = FALSE
               AND geocode_attempts <  %s
             LIMIT 10;
        """, (MAX_ATTEMPTS,))
        rows = cur.fetchall()
        if not rows:
            logger.info("No more records to geocode.")
            return

        for row in rows:
            pid      = row["id"]
            attempts = row["geocode_attempts"] + 1

            # bump attempt counter
            cur.execute("""
                UPDATE project_data
                   SET geocode_attempts = %s
                 WHERE id = %s;
            """, (attempts, pid))

            district = row.get("district") or ""
            address  = row.get("address")  or ""
            name     = row.get("name")     or ""
            query    = " ".join([district, address, name]).strip()

            lon_gcj, lat_gcj = geocode(query)
            if lon_gcj is None:
                if attempts >= MAX_ATTEMPTS:
                    cur.execute("""
                        UPDATE project_data
                           SET geocode_failed = TRUE
                         WHERE id = %s;
                    """, (pid,))
                    logger.warning("Project %s marked permanently failed after %s attempts.", pid, attempts)
                continue

            lon_wgs84, lat_wgs84 = gcj2wgs(lon_gcj, lat_gcj)
            cur.execute("""
                UPDATE project_data
                   SET lon_gcj02  = %s,
                       lat_gcj02  = %s,
                       lon_wgs84  = %s,
                       lat_wgs84  = %s,
                       geom_gcj02 = ST_SetSRID(ST_MakePoint(%s, %s), 4490),
                       geom_wgs84 = ST_SetSRID(ST_MakePoint(%s, %s), 4326)
                 WHERE id = %s;
            """, (
                lon_gcj, lat_gcj,
                lon_wgs84, lat_wgs84,
                lon_gcj, lat_gcj,
                lon_wgs84, lat_wgs84,
                pid
            ))
            logger.info(
                "Updated project %s %s with GCJ-02 (%.6f, %.6f) and WGS-84 (%.6f, %.6f)",
                pid, name, lon_gcj, lat_gcj, lon_wgs84, lat_wgs84
            )
            time.sleep(0.3)

        conn.commit()

# ── MAIN ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # one-time schema migration
    with psycopg2.connect(DATABASE_URL) as conn:
        ensure_tracking_columns(conn)

    if TESTING_FLAG:
        test_query = "黄浦区 新疆路518号 base苏河"
        logger.info("Testing geocode for: %s", test_query)
        lon_gcj, lat_gcj = geocode(test_query)
        if lon_gcj is not None:
            lon_wgs84, lat_wgs84 = gcj2wgs(lon_gcj, lat_gcj)
            logger.info(" → GCJ-02: %.6f, %.6f", lon_gcj, lat_gcj)
            logger.info(" → WGS-84: %.6f, %.6f", lon_wgs84, lat_wgs84)
    else:
        while True:
            try:
                with psycopg2.connect(DATABASE_URL) as conn:
                    update_project_data(conn)
            except Exception as e:
                logger.exception("Worker loop encountered fatal error: %s", e)
            time.sleep(SLEEP_SEC)