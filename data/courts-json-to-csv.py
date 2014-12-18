import json
import sys
import csv
import re

TAG_RE = re.compile(r'<[^>]+>')

def clean(s):
    return TAG_RE.sub('', s.replace('\n','')).replace('\r','')

if len(sys.argv) != 2:
    print("usage: %s <json-file>" % sys.argv[0])
    sys.exit(-1)

with open(sys.argv[1]) as f:
    courts = json.loads(f.read())

fieldnames = ['name','number', 'visiting_address', 'postal_address', 'contacts', 'emails', 'facilities', 'areas_of_law', 'court_types']
writer = csv.DictWriter(sys.stdout, fieldnames=fieldnames)

writer.writeheader()

for court in courts:

    visiting_address = ''
    for address in court['addresses']:
        if address['type'] == 'Visiting':
            visiting_address = "%s; %s; %s; %s" % (address['address'], address['town'], address['postcode'], address['county'])
            visiting_address = visiting_address
    postal_address = ''
    for address in court['addresses']:
        if address['type'] == 'Postal':
            postal_address = "%s; %s; %s; %s" % (address['address'], address['town'], address['postcode'], address['county'])
            postal_address = postal_address

    contacts = []
    for contact in court['contacts']:
        contacts.append("%s: %s" % (contact['name'], contact['number']))
    contacts = ';'.join(contacts)

    emails = []
    for email in court['emails']:
        emails.append("%s: %s" % (email['description'], email['address']))
    emails = ';'.join(emails)

    facilities = []
    for facility in court['facilities']:
        facilities.append("%s: %s" % (facility['name'], facility['description']))
    facilities = ';'.join(facilities)

    areas_of_law = []
    for aol in court['areas_of_law']:
        areas_of_law.append(aol['name'])
    areas_of_law = ';'.join(areas_of_law)

    court_types = ';'.join(court['court_types'])

    writer.writerow({'name': court['name'],
                     'number': court['court_number'],
                     'visiting_address': clean(visiting_address),
                     'postal_address': clean(postal_address),
                     'emails': clean(emails),
                     'contacts': clean(contacts),
                     'facilities': clean(facilities),
                     'areas_of_law': clean(areas_of_law),
                     'court_types': clean(court_types)
                 })
