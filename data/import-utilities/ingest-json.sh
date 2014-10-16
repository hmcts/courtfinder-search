#!/bin/bash
PYTHON=env/bin/python
DBNAME='courtfinder_search'
DBNAMETMP='courtfinder_search_tmp'
DBUSER='mf'
DBADMINUSER='mf'

psql -U $DBUSER template1 -c "CREATE DATABASE $DBNAMETMP WITH TEMPLATE $DBNAME OWNER $DBUSER;"
$PYTHON manage.py populate-db || { echo 'populate-db failed'; exit -1; }
psql -U $DBUSER template1 -c "DROP DATABASE $DBNAME; ALTER DATABASE $DBNAMETMP RENAME TO $DBNAME;"
echo 'Done.'

