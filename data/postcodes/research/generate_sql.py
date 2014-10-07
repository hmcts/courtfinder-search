import pprint
import re
import sys

import psycopg2
from pymongo import MongoClient

client = MongoClient()
db = client.postcodes

courts_la = {}

pp = pprint.PrettyPrinter(indent=4)

client = MongoClient()
db = client.postcodes

conn = psycopg2.connect("dbname='courtfinder_production' user='courtfinder' host='localhost'")


def main():
    sql_string = ""

    councils = {}

    all_las = set()
    missing_las = set()
    aol_ids = get_aol_ids()
    isles_of_scilly_courts = set()

    [all_las.update(set(row['local_authorities'])) for row in db.court_la_final.find()]

    for la in all_las:
        cur = conn.cursor()
        cur.execute("SELECT * FROM councils WHERE name = '%s'" % la)
        row = cur.fetchone()
        if row is None:
            missing_las.add(la)
        else:
            councils[row[1]] = row[0]


    all_courts = db.court_la_final.find()
    for row in all_courts:
        court = row['court']
        local_authorities = row['local_authorities']

        cur = conn.cursor()
        cur.execute("SELECT * FROM courts WHERE name = %s", [court])
        court_id = cur.fetchone()[0]

        for la in local_authorities:
            if la in councils:
                council_id = councils[la]

                for aol_id in aol_ids:
                    sql = """INSERT INTO court_council_links 
                                    (court_id, council_id, created_at, updated_at, area_of_law_id) 
                                VALUES 
                                    (%s, %s, now(), now(), %s);""" % (court_id, council_id, aol_id)
                    

                    sql_string += tidy_up_sql(sql) + '\n'

            else:
                if la == 'Isles of Scilly Council':
                    isles_of_scilly_courts.add(court_id)



    sql_string += """INSERT INTO councils (name, created_at, updated_at) VALUES ('Isles of Scilly Council', now(), now());""" + '\n'

    for court_id in isles_of_scilly_courts:
        for aol_id in aol_ids:
            sql = """INSERT INTO court_council_links 
                            (court_id, council_id, created_at, updated_at, area_of_law_id) 
                        VALUES 
                            (%s, (SELECT id FROM councils WHERE name like 'Isles of Scilly Council'), now(), now(), %s);""" % (court_id, aol_id)

            sql_string += tidy_up_sql(sql) + '\n'

    with open('out/update.sql', 'w') as fhandle:
        fhandle.write(sql_string)
        fhandle.close()



def tidy_up_sql( sql ):
    return re.sub( r'\s+', ' ', sql)

def get_aol_ids():
    cur = conn.cursor()
    cur.execute("SELECT * FROM areas_of_law WHERE name = 'Money claims'")
    money_claims_id = cur.fetchone()[0]
    cur.execute("SELECT * FROM areas_of_law WHERE name = 'Bankruptcy'")
    bankruptcy_id = cur.fetchone()[0]
    cur.execute("SELECT * FROM areas_of_law WHERE name = 'Housing possession'")
    housing_possession_id = cur.fetchone()[0]

    return [money_claims_id, bankruptcy_id, housing_possession_id]


def compile_courts():
    total_count = 0
    court_list = get_court_list()
    for court, postcodes in court_list.iteritems():
        court_la_set = set()
        for postcode in postcodes:
            postcode = format_postcode(postcode)

            mapit_council = mapit(postcode)
            if mapit_council is not False:
                court_la_set.add(mapit_council)
            else:
                qs = db.postcode_deduced_la.find_one({ "postcode": postcode })
                
                if qs is not None:
                    court_la_set.add(qs['local_authority'])
                else:
                    qm = db.postcodes_deduced_multi_la.find_one({ "postcode": postcode })
                    
                    if qm is not None:
                        court_la_set.update(set(qm['local_authorities']))

        if False in court_la_set:
            court_la_set.remove(False)

        db.court_la_final.update({ "court": court },
            {
                "court": court,
                "local_authorities": list(court_la_set)          
            },
            True)

        print court


def get_court_list():
    court_list = {}
    query = db.court_postcodes.find()
    for row in query:
        courtname = row['court']
        postcodes_covered = row['postcodes']

        if courtname in court_list:
            print "Duplication ", courtname
            court_list[courtname].append(postcodes_covered)
        else:
            court_list[courtname] = postcodes_covered

    return court_list


def mapit( postcode ):
    p = format_postcode(postcode)

    cache_check = db.mapit_response_cache.find_one({"postcode": p})
    if cache_check is not None:
        # print "++ %s retrieved from cache" % p
        data = cache_check['response']
    else:
        print "----> Not in cache: ", postcode
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