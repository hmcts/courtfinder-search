import json
import re
import sys
import time

from pymongo import MongoClient
import psycopg2
import requests

client = MongoClient()
db = client.postcodes

conn = psycopg2.connect("dbname='courtfinder_production' user='courtfinder' host='localhost'")

db_councils = set()
current_councils = set()

court_postcodes = {}
postcode_councils = {}

mapit_full_url = "http://mapit.mysociety.org/postcode/%s"
mapit_partial_url = "http://mapit.mysociety.org/postcode/partial/%s"


def main():
    court_la = {}

    for row in db.court_la.find():
        court_la[row['court']] = row['local_authorities']


    for row in db.court_postcodes.find():
        court_postcodes[row['court']] = row['postcodes']


    court = court_la.keys()[2]

    mapit_councils = set()

    for postcode in court_postcodes[court]:
        postcode = format_postcode(postcode)
        if len(postcode) > 4:
            mapit_council = mapit(postcode)
        else:
            mapit_council = mapit(postcode, 'partial')

        if mapit_council is not False:
            mapit_councils.add(mapit_council)


    pio_councils = court_la[court]

    matched_councils = set()
    unmatched_councils = set()
    multimatch = set()

    for pc in pio_councils:
        matched_set = filter(lambda x: x.find(pc), mapit_councils)



def mapit( postcode, ptype="full" ):
    if not (ptype == 'full' or ptype == 'partial'):
        print "MapIt type should be 'partial' or 'full', sent: %" % ptype
        return False

    p = format_postcode(postcode)

    url = (mapit_full_url, mapit_partial_url)[ptype == 'partial']
    r = requests.get(url % p)
    if r.status_code == 200:
        data = json.loads(r.text)
        
        if ptype == 'partial':
            return False

        if ptype == 'full':
            if type(data['shortcuts']['council']) == type({}):
                council_id = str(data['shortcuts']['council']['county'])
            else:
                council_id = str(data['shortcuts']['council'])

            return data['areas'][council_id]['name']
    else:
        if r.text.startswith('Rate limit'):
            print r.text
            sys.exit()
            return False
        else: 
            data = json.loads(r.text)
            print "%s - MapIt %s postcode Error: %s" % (postcode, ptype, data['error'])
            return False


def format_postcode( postcode ):
    return postcode.lower().replace(' ', '')


def courts_to_la():
    for row in db.court_postcodes.find():
        court = row['court']
        print court
        pcodes_for_court = [p.lower() for p in row['postcodes']]
        res = db.postcode_la.find({"postcode": {"$in": pcodes_for_court}})
        local_auths_for_court = set([prow['local_authority'] for prow in res])
        print local_auths_for_court 

        db.court_la.insert({
            "court": court,
            "local_authorities": list(local_auths_for_court)    
        })


def resolve_councils():
    cur = conn.cursor()
    cur.execute("SELECT * FROM councils")
    for row in cur.fetchall():
        db_councils.add(row[1])


    for a in db.postcode_la.find(fields=['local_authority']):
        current_councils.add(a['local_authority'])


    # matching_councils = set()
    # unmatched_councils = set()

    for cc in current_councils:
        if cc is not None:
            # match = [council for council in db_councils if council.startswith(cc)]
            match = [council for council in db_councils if cc in council]
            if len(match) != 1:
                print cc, len(match), match


    print [c for c in db_councils if "York" in c]

if __name__ == '__main__':
    main()

