#!/bin/bash
PYTHON=python

# Name of the temp database to be used to store data during import
DB_NAME_TMP="_tmp"

# Setup postgres pasword and args
export PGPASSWORD=${DB_PASSWORD}
PSQL_ARGS="-h ${DB_HOST} -p ${DB_PORT} -U ${DB_USERNAME} template1"

echo Dropping any temporary database if it exists
psql ${PSQL_ARGS} -c "DROP DATABASE IF EXISTS ${DB_NAME_TMP};"

echo Populating temporary database...
$PYTHON courtfinder/manage.py populate-db --database ${DB_NAME_TMP} --load-remote --sys-exit
if [ $? -eq 0 ]; then
	echo Creating temporary database...
	psql ${PSQL_ARGS} -c "CREATE DATABASE ${DB_NAME_TMP} WITH TEMPLATE ${DB_NAME} OWNER ${DB_USERNAME};"
	$PYTHON courtfinder/manage.py populate-db --database ${DB_NAME_TMP} --ingest --sys-exit
	if [ $? -eq 0 ]; then 
		echo Replacing ${DB_NAME} with newly populated database ${DB_NAME_TMP}...
		psql ${PSQL_ARGS} -c "DROP DATABASE IF EXISTS ${DB_NAME};"
		psql ${PSQL_ARGS} -c "ALTER DATABASE ${DB_NAME_TMP} RENAME TO ${DB_NAME};"
		echo 'Done.'
	else
	  echo "Failed ingesting files." >&2
	  psql ${PSQL_ARGS} -c "DROP DATABASE IF EXISTS ${DB_NAME_TMP};"
	  exit 1
	fi
else
	  echo "Failed loading files." >&2
	  exit 1
fi
