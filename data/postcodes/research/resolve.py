import itertools
import json
import random
import re
import sys
import time

import requests
from pymongo import MongoClient

client = MongoClient()
db = client.postcodes

mapit_full_url = "http://mapit.mysociety.org/postcode/%s"
mapit_partial_url = "http://mapit.mysociety.org/postcode/partial/%s"


def main():
    resolve_for_multi_councils()

def resolve_for_multi_councils():
    multi_councils_query = db.postcodes_io_bulk_response_cache.find({ "$where": "this.councils.length > 1" })
    multi_councils = [ ( row['postcode'], row['councils'] ) for row in multi_councils_query]

    donelist = [row['postcode'] for row in db.postcodes_deduced_multi_la.find()]
    difflist = [row for row in multi_councils if row[0] not in donelist]

    for postcode, councils in difflist:
        compiled_results = postcodes_io(postcode)
        mapit_councils = [mapit(random.choice(row['postcodes'])) for row in compiled_results]

        print postcode 

        db.postcodes_deduced_multi_la.update(
        { "postcode": postcode },
        {
            "postcode": postcode,
            "local_authorities": mapit_councils
        },
        True) # Upsert


def resolve_with_a_single_council():
    single_list = db.postcodes_io_bulk_response_cache.find({ "$where": "this.councils.length == 1" })
    all_postcodes = [row['postcode'] for row in single_list]
    donelist = [row['postcode'] for row in db.postcode_deduced_la.find()]
    difflist = [p for p in all_postcodes if p not in donelist]

    for postcode in difflist:
        obj = db.postcodes_io_autcomplete_cache.find_one({ "postcode": postcode })
        a_postcode = random.choice(obj['postcode_list'])

        council = mapit( a_postcode )

        print postcode, council

        db.postcode_deduced_la.insert({
            "postcode": postcode,
            "local_authority": council 
        })


def postcodes_harvest():
    mapit_fails = [row['postcode'] for row in db.mapit_response_cache.find({ "response.error": { "$exists": True } })]
    
    for postcode in mapit_fails:
        print "++++++ " + postcode
        councils = postcodes_io(postcode)

        print councils

        if councils is not False:
            db.postcodes_io_bulk_response_cache.insert({
                "postcode": postcode,
                "councils": list(councils)
            })



def first_run():
    for row in db.court_postcodes.find():
        court = row['court']
        postcodes = row['postcodes']

        for postcode in postcodes:
            print postcode
            council = mapit(postcode)
            print council


def postcodes_io( postcode ):
    p = format_postcode(postcode)

    r = requests.get( "http://api.postcodes.io/postcodes/%s/autocomplete?limit=100" % p )
    if r.status_code == 200:
        response = json.loads(r.text)
        postcode_list = response['result']
        db.postcodes_io_autcomplete_cache.update(
            { "postcode": postcode }, 
            {
                "postcode": postcode,
                "postcode_list": postcode_list
            },
            True ) #upsert
    else:
        print "----- Failed postcode autocomplete lookup"
        return False

    payload = { "postcodes": postcode_list }
    r = requests.post('http://api.postcodes.io/postcodes', data=payload )
    if r.status_code == 200:
        response = json.loads(r.text)
        council_set = [ (row['query'], get_council_from_postcodes_io_obj(row['result'])) 
                        for row in response['result']]

        sorted_set = sorted(council_set, key=lambda x: x[1])
        council_set = [{ "council": r[0], "postcodes": [p[0] for p in r[1]] } 
                        for r in itertools.groupby(sorted_set, lambda x: x[1])]

        return council_set
    else:
        print "------ Failed bulk lookup"
        print r.text
        return False



def get_council_from_postcodes_io_obj( obj ):
    if obj['admin_county'] is not None:
        return obj['admin_county']
    else:
        return obj['admin_district']



def mapit( postcode ):
    p = format_postcode(postcode)

    cache_check = db.mapit_response_cache.find_one({"postcode": p})
    if cache_check is not None:
        print "++ %s retrieved from cache" % p
        data = cache_check['response']
    else:
        r = requests.get(mapit_full_url % p)
        if r.status_code == 200:
            data = json.loads(r.text)

            print p

            db.mapit_response_cache.insert({
                "postcode": p,
                "response": data
            })

        else:
            if r.text.startswith('Rate limit'):
                print r.text, postcode
                print "Sleeping for 30 secs"
                time.sleep(30)
                return mapit(postcode)
            else:
                try:
                    data = json.loads(r.text)
                    db.mapit_response_cache.insert({
                        "postcode": p,
                        "response": data
                    })

                    print "%s - MapIt postcode Error: %s" % (postcode, data['error'])
                    return False
                except:
                    print "JSON couldn't parse"
                    print "WTF - ", r.status_code
                    print r.text
                    return False

    if 'error' not in data:
        if type(data['shortcuts']['council']) == type({}):
            council_id = str(data['shortcuts']['council']['county'])
        else:
            council_id = str(data['shortcuts']['council'])

        # Horrid hack - mapit doesn't have this data
        if council_id == '2251':
            return "Isles of Scilly Council"

        return data['areas'][council_id]['name']
    else:
        return False



def format_postcode( postcode ):
    return postcode.lower().replace(' ', '')


if __name__ == '__main__':
    main()
