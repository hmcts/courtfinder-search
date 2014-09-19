import psycopg2
import json, requests
import random

from itertools import izip_longest

conn = psycopg2.connect("dbname='courtfinder_production' user='courtfinder' host='localhost'")

postcodes_tried = {}
postcode_not_found = []
courts = {}
local_authorities = {}

mapit_full_url = "http://mapit.mysociety.org/postcode/%s"
mapit_partial_url = "http://mapit.mysociety.org/postcode/partial/%s"


def get_all_postcodes_db():
    cur = conn.cursor()
    cur.execute("""
        SELECT c.name, pc.postcode
          FROM postcode_courts as pc,
               courts as c
         WHERE pc.court_id = c.id
    """)

    rows = cur.fetchall()
    return [r for r in rows]


def get_all_postcodes():
    with open('out/all_pcodes.json', 'r') as postcode_file:
        all_ps = json.load(postcode_file)
        postcode_file.close()

    return all_ps


def write_to_json( filename, obj ):
    with open('out/%s.json' % filename, 'w') as outfile:
        json.dump(obj, outfile, indent=4, separators=(',', ': '))
        print "== out/%s.json written" % filename
        outfile.close()


def format_postcode( postcode ):
    return postcode.lower().replace(' ', '')


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
        data = json.loads(r.text)
        print "%s - MapIt %s postcode Error: %s" % (postcode, ptype, data['error'])
        return False




def postcodes_io_bulk( postcodes ):
    ps = [format_postcode(p) for p in postcodes]

    payload = { "postcodes": ps }
    r = requests.post('http://api.postcodes.io/postcodes', data=payload )

    if r.status_code == 200:
        response = json.loads(r.text)
        if response['status'] == 200:
            good_postcodes = {}
            bad_postcodes = []

            for result in response['result']:
                postcode = result['query']
                print postcode
                if result['result'] == None:
                    bad_postcodes.append(postcode)
                else: 
                    if result['result']['admin_county'] is not None:
                        council_name = result['result']['admin_county']
                    elif result['result'] is not None:
                        council_name = result['result']['admin_district']
                    else:
                        print "--> Neither: %s" % postcode
                        continue

                    good_postcodes[postcode] = council_name

            return {
                "good_postcodes": good_postcodes,
                "bad_postcodes": bad_postcodes
            }
        else:
            print "Postcodes.io Error: %s"  % r.status
            print r.text
            return {"good_postcodes": [],"bad_postcodes": []}
    else:
        print "Postcodes.io Error: %s" % r.text
        return {"good_postcodes": [],"bad_postcodes": []}


def postcodes_io_query( postcode ):
    print postcode
    p = format_postcode(postcode)

    r = requests.get("http://api.postcodes.io/postcodes?q=%s" % p )

    if r.status_code == 200:
        response = json.loads(r.text)
        if response['status'] == 200:
            if response['result'] is None:
                print "-- %s - Fail" % postcode
                return []

            all_councils = set()
            all_postcodes_for_partial = []

            for result in response['result']:
                if result['admin_county'] is not None:
                    council_name = result['admin_county']
                elif result['admin_district'] is not None:
                    council_name = result['admin_district']
                else:
                    print "--> Neither: %s" % postcode

                all_councils.add(council_name)
                all_postcodes_for_partial.append(result['postcode'])

            print "%s \t| %s\t| %s" % (postcode, all_postcodes_for_partial , all_councils)

            return all_councils

        else:
            print "Postcodes.io Error: %s"  % r.status
            print r.text

    else:
        print "Postcodes.io Error: %s" % r.text



if __name__ == '__main__':
    all_good = []
    all_councils = set()

    resolved = {}

    with open('pcodes_io/postcode_io_good.json', 'r') as fhandle:
        first_good_batch = json.load( fhandle)
        fhandle.close()
        all_good += first_good_batch.keys()
        all_councils.update(first_good_batch.values())

    with open('pcodes_multi/single_la.json', 'r') as fhandle:
        second_good_batch = json.load( fhandle)
        fhandle.close()
        all_good += second_good_batch.keys()
        all_councils.update(second_good_batch.values())

    for council in all_councils:
        cur = conn.cursor()
        cur.execute("SELECT * FROM councils WHERE name like '%%%s %%'" % council)

        rows = cur.fetchall()
        resolved[council] = [r[1] for r in rows]

    sorted_res = sorted([(r, resolved[r]) for r in resolved if r is not None], cmp=lambda x, y: len(y[1]) - len(x[1]))

    for r in sorted_res:
        print "%s\t\t%s"% ( len(r[1]), r)