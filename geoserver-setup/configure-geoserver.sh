#!/bin/sh
set -e

# These variables are taken directly from your docker-compose.yml
GEOSERVER_URL="http://geoserver:8080/geoserver"
GEOSERVER_USER="admin"
GEOSERVER_PASS="admin"

# These are the names we will create in GeoServer
WORKSPACE_NAME="shanghai_properties"
DATASTORE_NAME="cdh_mezz_postgis"
LAYER_NAME="dynamic_projects_view" # This MUST match the VIEW name in your SQL

echo "Waiting for GeoServer to be ready..."
until $(curl --output /dev/null --silent --head --fail -u "$GEOSERVER_USER:$GEOSERVER_PASS" "$GEOSERVER_URL/rest/workspaces"); do
    printf '.'
    sleep 5
done
echo "GeoServer is up and running!"

# 1. Create the Workspace
echo "Creating workspace '$WORKSPACE_NAME'..."
curl -u "$GEOSERVER_USER:$GEOSERVER_PASS" -XPOST -H "Content-type: text/xml" \
    -d "<workspace><name>$WORKSPACE_NAME</name></workspace>" \
    "$GEOSERVER_URL/rest/workspaces"

# 2. Create the PostGIS Data Store using your DB details
echo "Creating PostGIS datastore '$DATASTORE_NAME'..."
cat <<EOF > /tmp/datastore.xml
<dataStore>
  <name>${DATASTORE_NAME}</name>
  <connectionParameters>
    <host>postgres</host>
    <port>5432</port>
    <database>spatialdb</database>
    <user>admin</user>
    <passwd>admin</passwd>
    <dbtype>postgis</dbtype>
  </connectionParameters>
</dataStore>
EOF
curl -u "$GEOSERVER_USER:$GEOSERVER_PASS" -XPOST -H "Content-type: text/xml" \
    -d @/tmp/datastore.xml \
    "$GEOSERVER_URL/rest/workspaces/$WORKSPACE_NAME/datastores"

# 3. Publish the Layer from your SQL View
echo "Publishing layer '$LAYER_NAME'..."
cat <<EOF > /tmp/featuretype.xml
<featureType>
  <name>${LAYER_NAME}</name>
  <nativeName>${LAYER_NAME}</nativeName>
  <title>Dynamic Projects Layer</title>
  <srs>EPSG:4326</srs>
  <nativeBoundingBox>
    <minx>-180.0</minx> <maxx>180.0</maxx> <miny>-90.0</miny> <maxy>90.0</maxy>
    <crs>EPSG:4326</crs>
  </nativeBoundingBox>
  <latLonBoundingBox>
    <minx>-180.0</minx> <maxx>180.0</maxx> <miny>-90.0</miny> <maxy>90.0</maxy>
    <crs>EPSG:4326</crs>
  </latLonBoundingBox>
  <enabled>true</enabled>
</featureType>
EOF
curl -u "$GEOSERVER_USER:$GEOSERVER_PASS" -XPOST -H "Content-type: text/xml" \
    -d @/tmp/featuretype.xml \
    "$GEOSERVER_URL/rest/workspaces/$WORKSPACE_NAME/datastores/$DATASTORE_NAME/featuretypes"

echo "GeoServer configuration complete!"