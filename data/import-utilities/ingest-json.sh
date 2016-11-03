#!/bin/bash
PYTHON=python

MESSAGE_FORMAT="json"

# Name of the temp database to be used to store data during import
DB_NAME_TMP="_tmp"

# Setup postgres pasword and args
export PGPASSWORD=${DB_PASSWORD}
PSQL_ARGS="-h ${DB_HOST} -p ${DB_PORT} -U ${DB_USERNAME} template1"

hostname=$(hostname)
log(){
	message="$1"
	if [ ! -z $2 ]; then
		level=$2
	else
		level="INFO"
	fi
	if [ "x${MESSAGE_FORMAT}" = "xjson" ]; then
		echo "{\"hostname\":\""$hostname"\", \"timestamp\":\"$(date)\", \"message\":\""${message}"\", \"level\":\""${level}"\"}"
	else
		echo "$(date)" "${hostname}" "${message}" level: "${level}"
	fi
}
log "Dropping any temporary database if it exists"
result=$(psql ${PSQL_ARGS} -c "DROP DATABASE IF EXISTS ${DB_NAME_TMP};")
log "Result ${result}"

log "Populating temporary database..."
$PYTHON courtfinder/manage.py populate-db --database ${DB_NAME_TMP} --load-remote --sys-exit
POPULATE_EXIT_CODE=$?
if [ ${POPULATE_EXIT_CODE} -eq 200 ]; then
	# 200 exit code signifies no change
    log "SUCCESS: No update required"
    exit 0
elif [ ${POPULATE_EXIT_CODE} -eq 0 ]; then
	log "Creating temporary database..."
	result=$(psql ${PSQL_ARGS} -c "CREATE DATABASE ${DB_NAME_TMP} WITH TEMPLATE ${DB_NAME} OWNER ${DB_USERNAME};")
	log "Result ${result}"
	$PYTHON courtfinder/manage.py populate-db --database ${DB_NAME_TMP} --ingest --sys-exit
	if [ $? -eq 0 ]; then 
		log "Replacing ${DB_NAME} with newly populated database ${DB_NAME_TMP}..."
		result=$(psql ${PSQL_ARGS} -c "DROP DATABASE IF EXISTS ${DB_NAME};")
		log "Result ${result}"
		result=$(psql ${PSQL_ARGS} -c "ALTER DATABASE ${DB_NAME_TMP} RENAME TO ${DB_NAME};")
		log "Result ${result}"
		log "SUCCESS"
	else
	  log "Failed ingesting files."
	  result=$(psql ${PSQL_ARGS} -c "DROP DATABASE IF EXISTS ${DB_NAME_TMP};")
	  log "Result ${result}" "CRITICAL"
	  exit 1
	fi
else
	  log "Failed loading files." "CRITICAL"
	  exit 1
fi
