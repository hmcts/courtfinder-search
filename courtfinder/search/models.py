from django.db import models

class Court(models.Model):
    admin_id = models.IntegerField(null=True, default=None)
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    displayed = models.BooleanField(default=False)
    lat = models.FloatField(null=True)
    lon = models.FloatField(null=True)
    number = models.IntegerField(null=True)
    alert = models.CharField(max_length=4096, null=True, default=None)
    directions = models.CharField(max_length=4096, null=True, default=None)
    image_file = models.CharField(max_length=255, null=True, default=None)
    areas_of_law = models.ManyToManyField('AreaOfLaw', through='CourtAreaOfLaw', null=True)
    emails = models.ManyToManyField('Email', through='CourtEmail', null=True)
    attributes = models.ManyToManyField('CourtAttributeType', through='CourtAttribute', null=True)
    addresses = models.ManyToManyField('AddressType', through='CourtAddress', null=True)
    court_types = models.ManyToManyField('CourtType', through='CourtCourtType', null=True)
    facilities = models.ManyToManyField('Facility', through='CourtFacility', null=True)
    opening_times = models.ManyToManyField('OpeningTime', through='CourtOpeningTime', null=True)
    contacts = models.ManyToManyField('Contact', through='CourtContact', null=True)
    cci_code = models.CharField(max_length=255, null=True, default=None)
    updated_at = models.DateTimeField(null=True, default=None)
    created_at = models.DateTimeField(null=True, default=None)

    def postcodes_covered(self):
        return CourtPostcode.objects.filter(court=self)

    def __unicode__(self):
        return self.name


class CourtAttributeType(models.Model):
    name = models.CharField(max_length=255)

    def __unicode__(self):
        return self.name


class CourtAttribute(models.Model):
    court = models.ForeignKey(Court)
    attribute_type = models.ForeignKey(CourtAttributeType)
    value = models.TextField()

    def __unicode__(self):
        return "%s.%s = %s" % (self.court.name, self.attribute_type.name, self.value)


class CourtPostcode(models.Model):
    court = models.ForeignKey(Court)
    postcode = models.CharField(max_length=250)

    def __unicode__(self):
        return "%s covers %s" % (self.court.name, self.postcode)


class AreaOfLaw(models.Model):
    name = models.CharField(max_length=255)

    def __unicode__(self):
        return self.name

class Facility(models.Model):
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=4096)
    image = models.CharField(max_length=255)
    image_description = models.CharField(max_length=255)

    def __unicode__(self):
        return "%s: %s" % (self.name, self.description)

class OpeningTime(models.Model):
    description = models.CharField(max_length=1024)

    def __unicode__(self):
        return self.description


class LocalAuthority(models.Model):
    name = models.TextField()

    def __unicode__(self):
        return self.name


class CourtLocalAuthorityAreaOfLaw(models.Model):
    court = models.ForeignKey(Court)
    area_of_law = models.ForeignKey(AreaOfLaw)
    local_authority = models.ForeignKey(LocalAuthority)

    def __unicode__(self):
        return "%s covers %s for %s" % (self.court.name, self.local_authority.name, self.area_of_law.name)

class CourtFacility(models.Model):
    court = models.ForeignKey(Court)
    facility = models.ForeignKey(Facility)

    def __unicode__(self):
        return "%s has facility %s" % (self.court.name, self.facility)

class CourtOpeningTime(models.Model):
    court = models.ForeignKey(Court)
    opening_time = models.ForeignKey(OpeningTime)

    def __unicode__(self):
        return "%s has facility %s" % (self.court.name, self.opening_time)

class CourtAreaOfLaw(models.Model):
    court = models.ForeignKey(Court)
    area_of_law = models.ForeignKey(AreaOfLaw)

    def local_authorities_covered(self):
        return CourtLocalAuthorityAreaOfLaw.objects.filter(
            court=self.court,
            area_of_law=self.area_of_law
        )

    def __unicode__(self):
        return "%s deals with %s" % (self.court.name, self.area_of_law.name)


class Town(models.Model):
    name = models.CharField(max_length=255)
    county = models.ForeignKey('County')

    def __unicode__(self):
        return self.name


class County(models.Model):
    name = models.CharField(max_length=255)
    country = models.ForeignKey('Country')

    def __unicode__(self):
        return self.name


class Country(models.Model):
    name = models.CharField(max_length=255)

    def __unicode__(self):
        return self.name


class AddressType(models.Model):
    name = models.CharField(max_length=255)

    def __unicode__(self):
        return self.name


class CourtAddress(models.Model):
    address_type = models.ForeignKey(AddressType)
    court = models.ForeignKey(Court)
    address = models.TextField()
    postcode = models.CharField(max_length=255)
    town = models.ForeignKey(Town)

    def __unicode__(self):
        return "%s for %s is %s, %s, %s" % (self.address_type.name, self.court.name, self.address, self.postcode, self.town.name)


class Contact(models.Model):
    name = models.CharField(max_length=255)
    number = models.CharField(max_length=255)

    def __unicode__(self):
        return "%s: %s" % (self.name, self.number)


class CourtContact(models.Model):
    contact = models.ForeignKey(Contact)
    court = models.ForeignKey(Court)

    def __unicode__(self):
        return "%s for %s is %s" % (self.contact.name, self.court.name, self.contact.number)


class Email(models.Model):
    description = models.CharField(max_length=255)
    address = models.CharField(max_length=255)

    def __unicode__(self):
        return self.description


class CourtEmail(models.Model):
    court = models.ForeignKey(Court)
    email = models.ForeignKey(Email)

    def __unicode__(self):
        return "%s has email: %s" % (self.court.name, self.email.description)


class CourtType(models.Model):
    name = models.CharField(max_length=255)

    def __unicode__(self):
        return self.name


class CourtCourtType(models.Model):
    court = models.ForeignKey(Court)
    court_type = models.ForeignKey(CourtType)

    def __unicode__(self):
        return "Court type for %s is %s" % (self.court.name, self.court_type.name)


class DataStatus(models.Model):
    data_hash = models.CharField(max_length=255)
    last_ingestion_date = models.DateTimeField(auto_now=True, auto_now_add=True)

    def __unicode__(self):
        return "Current data hash: %s, last update: %s" % (self.data_hash, self.last_ingestion_date)
