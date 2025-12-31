#!/bin/sh
set -e

# install once
apk add --no-cache postgresql15-client curl >/dev/null

echo "🔍 Auto-publish started ..."
while true; do
  # --- 1. list every *user* view with a geometry column -------------
  views=$(psql -At <<'SQL'
SELECT v.table_name
FROM information_schema.views v
JOIN geometry_columns g
  ON g.f_table_schema = v.table_schema
 AND g.f_table_name   = v.table_name
WHERE v.table_schema = 'public'
  AND v.table_name   NOT LIKE 'geography_%'
  AND v.table_name   NOT LIKE 'geometry_%';
SQL
)

  for v in $views; do
    # --- 2. skip if GeoServer layer already exists ------------------
    code=$(curl -s -o /dev/null -w '%{http_code}' -u "$GEOSERVER_USER:$GEOSERVER_PASS" \
           "$GEOSERVER_URL/rest/layers/$WORKSPACE:$v.xml")
    if [ "$code" = "200" ]; then
      echo "✅ $v already published"
      continue
    fi

    echo "➕ Publishing $v ..."
    cat > /tmp/ft.xml <<EOF
<featureType>
  <name>$v</name>
  <nativeName>$v</nativeName>
  <srs>EPSG:4326</srs>
  <enabled>true</enabled>
</featureType>
EOF
    curl -s -u "$GEOSERVER_USER:$GEOSERVER_PASS" -XPOST \
         -H "Content-Type: text/xml" -d @/tmp/ft.xml \
         "$GEOSERVER_URL/rest/workspaces/$WORKSPACE/datastores/$DATASTORE/featuretypes"
  done

  sleep 60   # check again in one minute
done