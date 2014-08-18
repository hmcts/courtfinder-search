import psycopg2
from search.models import Court, AreaOfLaw, CourtAreasOfLaw

def imp():
    conn = psycopg2.connect("dbname='courtfinder_development' user='courtfinder' host='localhost'")
    cur = conn.cursor()
    cur.execute("SELECT name, court_number, slug, latitude, longitude FROM Courts")
    rows = cur.fetchall()

    for row in rows:
        name, court_number, slug, lat, lon = row

        if name == None or slug == None or lat == None or lon == None:
            print name
            continue

        cur = conn.cursor()
        sql = """SELECT a.name
                  FROM courts as c, areas_of_law as a, courts_areas_of_law as ac
                 WHERE ac.court_id = c.id
                  AND ac.area_of_law_id = a.id
                  AND c.slug = '%s'""" % slug

        cur.execute(sql)
        aols_raw = cur.fetchall()

        c = Court( name=name, slug=slug, lat=lat, lon=lon, displayed=True)
        c.save()

        for aol in aols_raw:
            a = AreaOfLaw.objects.get(name=aol[0])
            ac = CourtAreasOfLaw(court=c, area_of_law=a)
            ac.save()

        print name
