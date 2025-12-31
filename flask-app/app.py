import os
import psycopg2
from psycopg2.extras import RealDictCursor
from flask import Flask, jsonify, request

DATABASE_URL = os.getenv("DATABASE_URL")
AMAP_KEY     = os.getenv("AMAP_KEY", "")
SECRET_KEY   = os.getenv("SECRET_KEY", "dev-secret")

app = Flask(__name__)
app.config["SECRET_KEY"] = SECRET_KEY

# ──────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────

def get_conn():
    """Return a new DB connection using RealDictCursor."""
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

# ──────────────────────────────────────────────────────────────
# End‑points: Locations
# ──────────────────────────────────────────────────────────────

@app.route("/locations/<int:loc_id>")
def get_location(loc_id):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """
            SELECT id,
                   address,
                   ST_AsGeoJSON(location) AS geometry
              FROM customer_locations
             WHERE id = %s;
            """,
            (loc_id,),
        )
        row = cur.fetchone()
    if not row:
        return jsonify({"error": "Not found"}), 404
    return jsonify(row)


@app.route("/locations/by_address")
def get_location_by_addr():
    addr = request.args.get("address", "").strip()
    if not addr:
        return jsonify({"error": "address param required"}), 400
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """
            SELECT id,
                   address,
                   ST_AsGeoJSON(location) AS geometry
              FROM customer_locations
             WHERE address ILIKE %s
             LIMIT 1;
            """,
            (f"%{addr}%",),
        )
        row = cur.fetchone()
    if not row:
        return jsonify({"error": "Not found"}), 404
    return jsonify(row)


@app.route("/locations/batch", methods=["POST"])
def batch_locations():
    payload = request.get_json(force=True)
    ids  = payload.get("ids")
    addrs = payload.get("addresses")
    results = []

    with get_conn() as conn, conn.cursor() as cur:
        if ids:
            cur.execute(
                """
                SELECT id, address, ST_AsGeoJSON(location) AS geometry
                  FROM customer_locations
                 WHERE id = ANY(%s);
                """,
                (ids,),
            )
            results = cur.fetchall()
        elif addrs:
            for addr in addrs:
                cur.execute(
                    """
                    SELECT id, address, ST_AsGeoJSON(location) AS geometry
                      FROM customer_locations
                     WHERE address ILIKE %s
                     LIMIT 1;
                    """,
                    (f"%{addr}%",),
                )
                row = cur.fetchone()
                if row:
                    results.append(row)
    return jsonify(results)

# ──────────────────────────────────────────────────────────────
# End‑point:  spatial query – competitors within radius (km)
# Assumes a table `competitors(id, name, address, location geometry(Point,4326))`
# ──────────────────────────────────────────────────────────────

@app.route("/competitors/within_radius", methods=["POST"])
def competitors_within_radius():
    data = request.get_json(force=True)
    center_id   = data.get("center_id")
    center_addr = data.get("center_addr")
    radius_km   = float(data.get("radius_km", 0))

    if radius_km <= 0:
        return jsonify({"error": "radius_km must be > 0"}), 400

    with get_conn() as conn, conn.cursor() as cur:
        # Step 1: get center geometry in EPSG:3857 (metres)
        if center_id:
            cur.execute(
                "SELECT ST_Transform(location, 3857) FROM customer_locations WHERE id = %s;",
                (center_id,),
            )
        elif center_addr:
            cur.execute(
                """
                SELECT ST_Transform(location, 3857)
                  FROM customer_locations
                 WHERE address ILIKE %s
                 LIMIT 1;
                """,
                (f"%{center_addr}%",),
            )
        else:
            return jsonify({"error": "center_id or center_addr required"}), 400

        row = cur.fetchone()
        if not row or not row["st_transform"]:
            return jsonify({"error": "Center not found"}), 404

        center_3857 = row["st_transform"]  # geometry
        buffer_m = radius_km * 1000

        # Step 2: query competitors within buffer
        cur.execute(
            """
            WITH buf AS (
                SELECT ST_Buffer(%s::geometry, %s) AS geom
            )
            SELECT id,
                   name,
                   address,
                   ST_AsGeoJSON(ST_Transform(location, 4326)) AS geometry
              FROM competitors, buf
             WHERE ST_DWithin(
                     ST_Transform(location, 3857),
                     buf.geom,
                     %s
                   );
            """,
            (center_3857, buffer_m, buffer_m),
        )
        competitors = cur.fetchall()
    return jsonify(competitors)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)