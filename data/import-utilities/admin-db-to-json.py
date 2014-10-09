import psycopg2
import json

conn = psycopg2.connect("dbname='courtfinder_development' user='courtfinder' host='localhost'")

# these descriptions are found in the admin app's locale files, not in the database
parking_types = {"parking_onsite_free": "Free, on site parking is available, provided by the court.",
                 "parking_onsite_paid": "Paid, on site parking is available, provided by the court.",
                 "parking_offsite_free": "Free parking is available within a 5 minute walk.",
                 "parking_offsite_paid": "Paid parking is available within a 5 minute walk.",
                 "parking_none": "No parking facilities are available at or near the court.",
                 "parking_onsite_none": "No parking facilities are available at or near the court."}

def courts():
    all_courts = []

    cur = conn.cursor()
    cur.execute("SELECT id, name, display, court_number, slug, latitude, longitude, image_file, alert, parking_onsite, parking_offsite FROM courts")
    rows = cur.fetchall()

    for row in rows:
        admin_id, name, display, court_number, slug, lat, lon, image_file, alert, parking_onsite, parking_offsite = row

        if name == None or slug == None:
            print "- %s\n\tslug: %s, lat: %s, lon: %s" % (name, slug, lat, lon)
            continue

        aols = areas_of_law_for_court(slug)
        addresses = addresses_for_court(slug)
        court_types = court_types_for_court(slug)
        contacts = contacts_for_court(slug)
        postcodes = postcodes_for_court(slug)
        facilities = facilities_for_court(slug)
        opening_times = opening_times_for_court(slug)
        parking = {}
        if parking_onsite is not None:
            parking["onsite"] =  parking_types[parking_onsite]
        if parking_offsite is not None:
            parking["offsite"] =  parking_types[parking_offsite]


        court_object = {
            "admin_id": admin_id,
            "name": name,
            "display": display,
            "court_number": court_number,
            "slug": slug,
            "areas_of_law": aols,
            "addresses": addresses,
            "court_types": court_types,
            "contacts": contacts,
            "facilities": facilities,
            "postcodes": postcodes,

        }
        if lat is not None:
            court_object['lat'] = str(lat)
        if lon is not None:
            court_object['lon'] = str(lon)
        if image_file is not None:
            court_object['image_file'] = image_file
        if opening_times is not None:
            court_object['opening_times'] = opening_times
        if alert is not None:
            court_object['alert'] = alert
        if len(parking) > 0:
            court_object['parking'] = parking

        all_courts.append(court_object)
        print "+ %s" % name


    write_to_json( 'courts', all_courts )


def contacts_for_court( slug ):
    # contacts for court
    cur = conn.cursor()
    sql = """SELECT c.slug, ct.name as contact_type, co.telephone, co.sort
               FROM courts as c,
                    contact_types ct,
                    contacts co
              WHERE co.court_id = c.id
                AND co.contact_type_id = ct.id
                AND c.slug = '%s'""" % slug

    cur.execute(sql)
    contacts = [{
        "type": r[1],
        "number": r[2],
        "sort": r[3]
    } for r in cur.fetchall()]

    return contacts


def facilities_for_court( slug ):
    cur = conn.cursor()
    sql = """SELECT c.slug, cf.description, f.name, f.image, f.image_description
               FROM courts as c,
                    facilities f,
                    court_facilities cf
              WHERE cf.court_id = c.id
                AND cf.facility_id = f.id
                AND c.slug = '%s'""" % slug
    cur.execute(sql)
    facilities = [{
        "description": r[1],
        "name": r[2],
        "image": r[3],
        "image_description": r[4]
    } for r in cur.fetchall()]
    return facilities

def opening_times_for_court( slug ):
    cur = conn.cursor()
    sql = """SELECT ot.name, ott.name
               FROM opening_times as ot, courts as c, opening_types as ott
              WHERE ot.court_id = c.id
                AND ott.id = ot.opening_type_id
                AND c.slug = '%s'""" % slug
    cur.execute(sql)
    opening_times = [ r[1]+': '+r[0] for r in cur.fetchall()]
    return opening_times

def court_types_for_court( slug ):
    # court types for court
    cur = conn.cursor()
    sql = """SELECT ct.name as court_type
               FROM courts as c,
                    court_types ct,
                    court_types_courts ctc
              WHERE ctc.court_id = c.id
                AND ctc.court_type_id = ct.id
                AND c.slug = '%s'""" % slug

    cur.execute(sql)
    court_types =  [c[0] for c in cur.fetchall()]

    return court_types


def areas_of_law_for_court( slug ):
    # areas of law for court
    cur = conn.cursor()
    sql = """SELECT a.name
               FROM courts as c, areas_of_law as a, courts_areas_of_law as ac
              WHERE ac.court_id = c.id
                AND ac.area_of_law_id = a.id
                AND c.slug = '%s'""" % slug

    cur.execute(sql)
    aol_list = [a[0] for a in cur.fetchall()]

    aols = []
    for aol_name in aol_list:
        cur = conn.cursor()
        sql = """SELECT co.name
                   FROM court_council_links as ccl,
                        areas_of_law as aol,
                        courts as c,
                        councils as co
                  WHERE ccl.court_id = c.id
                    AND ccl.area_of_law_id = aol.id
                    AND ccl.council_id = co.id
                    AND c.slug = '%s'
                    AND aol.name = '%s'""" % (slug, aol_name)

        cur.execute(sql)
        councils = [c[0] for c in cur.fetchall()]

        aols.append({
            "name": aol_name,
            "councils": councils
        })

    return aols


def postcodes_for_court( slug ):
    cur = conn.cursor()
    sql = """SELECT pc.postcode
               FROM postcode_courts pc,
                    courts c
              WHERE pc.court_id = c.id
                AND c.slug = '%s'""" % slug

    cur.execute(sql)
    postcodes = [p[0] for p in cur.fetchall()]

    return postcodes
def addresses_for_court( slug ):
    # addresses for court
    cur = conn.cursor()
    sql = """SELECT t.name as town,
                    at.name as address_type,
                    a.address_line_1,
                    a.address_line_2,
                    a.address_line_3,
                    a.address_line_4,
                    a.postcode
               FROM courts as c,
                    address_types as at,
                    addresses as a,
                    towns as t
              WHERE a.court_id = c.id
                AND a.address_type_id = at.id
                AND a.town_id = t.id
                AND c.slug = '%s'""" % slug

    cur.execute(sql)
    addresses = [{
        "type": row[1],
        "address" : "\n".join([row[2], row[3], row[4], row[5]]),
        "postcode": row[6],
        "town": row[0],
    } for row in cur.fetchall()]
    return addresses



def areas_of_law():
    cur = conn.cursor()
    cur.execute("SELECT name, slug FROM areas_of_law")
    rows = cur.fetchall()

    all_aols = [{"name": name, "slug": slug } for name, slug in rows]
    write_to_json( 'areas_of_law', all_aols )


def court_types():
    cur = conn.cursor()
    cur.execute("SELECT name, slug FROM court_types")
    rows = cur.fetchall()

    all_court_types = [{"name": name, "slug": slug } for name, slug in rows]
    write_to_json( 'court_types', all_court_types )


def town_county_country():
    cur = conn.cursor()
    cur.execute("SELECT id, name FROM countries")

    countries = []
    country_names = cur.fetchall()

    for country_id, country_name in country_names:
        cur.execute("""SELECT co.id, co.name
                         FROM countries as c,
                              counties as co
                        WHERE co.country_id = c.id
                          AND c.id = %s""" % country_id )

        counties = []
        county_names = cur.fetchall()
        for county_id, county_name in county_names:
            cur.execute("""SELECT t.name
                             FROM counties as c,
                                  towns as t
                            WHERE t.county_id = c.id
                              AND c.id = %s""" % county_id)

            towns = [r[0] for r in cur.fetchall()]
            counties.append({
                "name": county_name,
                "towns": towns
            })

        countries.append({
            "name": country_name,
            "counties": counties
        })

    write_to_json("countries", countries)


def write_to_json( filename, obj ):
    with open('../%s.json' % filename, 'w') as outfile:
        json.dump(obj, outfile, indent=4, separators=(',', ': '))
        print "== ../%s.json written" % filename
        outfile.close()



if __name__ == '__main__':
    courts()
    areas_of_law()
    court_types()
    town_county_country()
