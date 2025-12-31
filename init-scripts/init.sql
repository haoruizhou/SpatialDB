-- initdb/init.sql

CREATE EXTENSION IF NOT EXISTS postgis;
-- 1. Create the table with all columns and appropriate types:
CREATE TABLE project_data (
  id                           INTEGER      PRIMARY KEY,
  comparability                TEXT,
  name                         TEXT,
  district                     TEXT,
  address                      TEXT,
  distance_to_target_km        NUMERIC,

  metro                        TEXT,
  owner_operator               TEXT,
  owner_operator_background    TEXT,
  total_rooms                  INTEGER,
  room_type                    TEXT,
  min_area                     NUMERIC,
  max_area                     NUMERIC,
  min_price                    NUMERIC,
  max_price                    NUMERIC,
  studio_count                 INTEGER,
  studio_min_area              NUMERIC,
  studio_max_area              NUMERIC,
  studio_min_price             NUMERIC,
  studio_max_price             NUMERIC,
  one_bedroom_count            INTEGER,
  one_bedroom_min_area         NUMERIC,
  one_bedroom_max_area         NUMERIC,
  one_bedroom_min_price        NUMERIC,
  one_bedroom_max_price        NUMERIC,
  two_bedroom_count            INTEGER,
  two_bedroom_min_area         NUMERIC,
  two_bedroom_max_area         NUMERIC,
  two_bedroom_min_price        NUMERIC,
  two_bedroom_max_price        NUMERIC,
  three_bedroom_count          INTEGER,
  three_bedroom_min_area       NUMERIC,
  three_bedroom_max_area       NUMERIC,
  three_bedroom_min_price      NUMERIC,
  three_bedroom_max_price      NUMERIC,
  sqm_efficiency               NUMERIC,
  occupancy_rate               NUMERIC,
  building_type                TEXT,
  num_floors                   TEXT,
  net_area_ratio               NUMERIC,
  renovation_level             TEXT,
  notes                        TEXT,
  contact_name                 TEXT,
  contact_info                 TEXT,
  lon_wgs84                    DOUBLE PRECISION,
  lat_wgs84                    DOUBLE PRECISION,
  lon_gcj02                  DOUBLE PRECISION,
    lat_gcj02                  DOUBLE PRECISION,
    geom_wgs84                GEOMETRY(Point, 4326),
    geom_gcj02                 GEOMETRY(Point, 4490),
    created_at                  TIMESTAMP DEFAULT CURRENT_TIMESTAMP


);

-- 2. Import the CSV (must match these column names exactly, in this order):
COPY project_data (
  id, comparability, name, district, address, distance_to_target_km, metro, owner_operator, owner_operator_background,
  total_rooms, room_type, min_area, max_area, min_price, max_price,
  studio_count, studio_min_area, studio_max_area, studio_min_price, studio_max_price,
  one_bedroom_count, one_bedroom_min_area, one_bedroom_max_area, one_bedroom_min_price, one_bedroom_max_price,
  two_bedroom_count, two_bedroom_min_area, two_bedroom_max_area, two_bedroom_min_price, two_bedroom_max_price,
  three_bedroom_count, three_bedroom_min_area, three_bedroom_max_area, three_bedroom_min_price, three_bedroom_max_price,
  sqm_efficiency, occupancy_rate, building_type, num_floors, net_area_ratio, renovation_level,
  notes, contact_name, contact_info, lon_wgs84, lat_wgs84, lon_gcj02, lat_gcj02
)
FROM '/docker-entrypoint-initdb.d/comparable_products.csv'
DELIMITER ','
CSV HEADER;


-- 3. Update geometry column from lon/lat
-- This ensures the geometry column is populated from your CSV data
UPDATE project_data SET geom_wgs84 = ST_SetSRID(ST_MakePoint(lon_wgs84, lat_wgs84), 4326);

-- 4. Create the dynamic VIEW that GeoServer will use
-- This is the part you will edit later in pgAdmin to change the map
CREATE OR REPLACE VIEW public.dynamic_projects_view AS
SELECT
    id,          -- Must include the primary key
    name,
    comparability,
    address,
    geom_wgs84   -- Must include the geometry column
FROM
    public.project_data
WHERE
    district LIKE '%静安%';  -- Initial filter, change this query later