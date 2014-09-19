declare -a collections=( \
    "court_la" \
    "court_postcodes" \
    "failed_postcodes" \
    "mapit_response_cache" \
    "multi_la_postcodes" \
    "postcode_deduced_la" \
    "postcode_la" \
    "postcodes_deduced_multi_la" \
    "postcodes_io_autcomplete_cache" \
    "postcodes_io_bulk_response_cache" \
)

for collection in "${collections[@]}"
do
	mongoimport --db postcodes --collection $collection --file $collection.json
done
