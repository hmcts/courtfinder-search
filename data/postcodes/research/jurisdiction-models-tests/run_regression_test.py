"""
This script compares the two jurisdiction models for courtfinder: postcodes and local authorities.
It runs postcodes in two instances of courtfinder and logs if the results match.
The area of law and geographical regions on which to run the postcodes can be selected below
"""

import json
import random
import sys
import time

import requests

# courtfinder instances to compare
# one should be set to search by postcode
# the other to search by local authority
cf_search_url = "http://127.0.0.1:8000/search/results.json?spoe=continue&postcode=%s&aol=%s"
cf_old_url = "https://courttribunalfinder.service.gov.uk/search/results.json?spoe=continue&postcode=%s&aol=%s"

# number of postcodes to try for each test
num_postcodes = int(sys.argv[1])

# how long to sleep between postcodes (so as not to overload mapit)
sleep_average = 0.25 # seconds

####################################################################################################

def main():
    compare_for(['Bankruptcy', 'Housing possession', 'Money claims'], ['london'], 'london_civil')
    compare_for(['Bankruptcy', 'Housing possession', 'Money claims'], ['england', 'wales', 'scotland'], 'all_civil')



def compare_for(aols, regions, test_name):
    # regions is a subset of ['london', 'wales', 'scotland', 'broken']
    # aols is a subset of ['Bankruptcy', 'Housing possession', 'Money claims'...]
    all_postcodes = []
    for region in regions:
        with open(region+'_postcodes.txt', 'r') as fhandle:
            postcodes = fhandle.read().split('\n')
            fhandle.close()
        all_postcodes += postcodes

    test_postcodes( all_postcodes, aols, test_name )


def test_postcodes( all_postcodes, areas_of_law, test_name ):

    print('========================================')
    print('running postcodes for ' + test_name)


    same_results = []
    different_results = []
    failed_lookups = []

    postcodes = random.sample(all_postcodes, num_postcodes)

    total_postcodes = len(postcodes)
    tested_postcodes = 0

    for postcode in postcodes:
        for area_of_law in areas_of_law:
            old_results = cf_search(postcode, area_of_law, cf_old_url)
            new_results = cf_search(postcode, area_of_law, cf_search_url)

            if len(old_results) > 0 and len(new_results) > 0:
                if old_results[0] == new_results[0]:

                    same_results.append({
                        "postcode": postcode,
                        "area_of_law": area_of_law,
                        "old_results": old_results,
                        "new_results": new_results
                    })
                else:

                    different_results.append({
                        "postcode": postcode,
                        "area_of_law": area_of_law,
                        "old_results": old_results,
                        "new_results": new_results
                    })

            else:
                failed_lookups.append({
                    "postcode": postcode,
                    "area_of_law": area_of_law
                })

            sys.stdout.flush()
            time.sleep(random.uniform(sleep_average - .15, sleep_average + 0.15))

        tested_postcodes += 1
        num_results = len(same_results)+len(different_results)
        ratio = float(len(same_results))/float(num_results) if num_results else 0
        sys.stdout.write("Tested %d / %d postcodes. %.2f success ratio so far\r" % (tested_postcodes, total_postcodes, ratio))
        sys.stdout.flush()

    print "\nTest complete."

    total_count = (len(same_results) + len(different_results))

    print "Tested %d random postcodes on %d areas of law (total: %d postcodes)." % (len(postcodes), len(areas_of_law), len(postcodes)*len(areas_of_law))
    print "%s postcodes gave the same results." % len(same_results)
    print "%s postcodes gave different results." % len(different_results)
    print "%s failures (probably mapit overload)." % len(failed_lookups)
    print "%.2f%% same/total ratio." % (float(len(same_results))/float(total_count)*100)

    generate_log(test_name, same_results, different_results, failed_lookups)


def cf_search( postcode, area_of_law, endpoint ):
    url = endpoint % (format_postcode( postcode ), area_of_law)
    r = requests.get(url, verify=False)
    if r.status_code == 200:
        response = json.loads(r.text)
        return [result['name'] for result in response]
    else:
        return []


def format_postcode( postcode ):
    return postcode.replace(' ', '+')


def generate_log( test_type, same_results, different_results, failed_lookups ):
    total_count = len(same_results) + len(different_results)

    log_obj = {
        "stats": {
            "total postcodes": total_count,
            "same results": len(same_results),
            "different results": len(different_results),
            "failed lookups": len(failed_lookups),
            "success_rate": round((float(len(same_results))/float(total_count)*100), 2)
        },
        "log": {
            "same results": same_results,
            "different results": different_results,
            "failed lookups": failed_lookups
        }
    }

    filename = 'logs/' + test_type + ' ' + time.strftime('%Y%m%d-%H:%M:%S') + '.log'
    filename = filename.replace(' ', '-')


    with open(filename, 'w') as fhandle:
        json.dump(log_obj, fhandle,  indent=4, separators=(',', ': '))
        fhandle.close()

    print "Log written: ", filename


if __name__ == '__main__':
    main()
