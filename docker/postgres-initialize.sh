#!/bin/bash
echo "***** INSTALLING POSTGIS EXTENSIONS *****"
POSTGRES="gosu postgres postgres"
$POSTGRES --single -E <<EOSQL
  CREATE DATABASE template_postgis;
  UPDATE pg_database SET datistemplate = TRUE WHERE datname = 'template_postgis';
EOSQL
POSTGIS_CONFIG=/usr/share/postgresql/9.4/contrib/postgis-2.1
$POSTGRES --single template_postgis -j < $POSTGIS_CONFIG/postgis.sql
$POSTGRES --single template_postgis -j < $POSTGIS_CONFIG/topology.sql
$POSTGRES --single template_postgis -j < $POSTGIS_CONFIG/spatial_ref_sys.sql

$POSTGRES -E <<EOSQL
  CREATE EXTENSION postgis;
  CREATE EXTENSION postgis_topology;
EOSQL
echo ""
echo "***** INSTALLED POSTGIS EXTENSIONS *****"
echo ""
echo "***** CLEANING UP *****"
rm /var/lib/postgresql/postmaster.pid