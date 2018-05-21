#!/bin/bash
PYTHON=python

if [ "$1" != "migration-override" ]; then
  # disable import for new admin, unless it's manual override
  echo "Import disabled for new admin, quitting..."
  exit 0
fi

MESSAGE_FORMAT="json"

# Name of the temp database to be used to store data during import
DB_NAME_TMP="_tmp"

# Marker file for healthy ingestion status. This will exist
# if the application considers the last ingestion completed 
# to have been successful
INGESTION_SUCCESS_FILE="last_ingestion_successful"

# The default courts data file path
COURTS_DATA_FILE="data/courts.json"

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

# If the last import was unsuccessful, remove the last courts data and try again.
if [ ! -f ${INGESTION_SUCCESS_FILE} ]; then
    log "Data uploaded but previous import was unsuccessful" "INFO"
    rm -f ${COURTS_DATA_FILE}
    rm -f ${INGESTION_SUCCESS_FILE}
fi

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
		touch ${INGESTION_SUCCESS_FILE}
	else
        rm -f ${INGESTION_SUCCESS_FILE}
        log "Failed import the data files into the database."
        result=$(psql ${PSQL_ARGS} -c "DROP DATABASE IF EXISTS ${DB_NAME_TMP};")
        log "Result ${result}" "CRITICAL"
        exit 1
	fi
else
    # The data was not loaded successfully into the application
    rm -f ${INGESTION_SUCCESS_FILE}
    log "Failed loading files." "CRITICAL"
    exit 1
fi
