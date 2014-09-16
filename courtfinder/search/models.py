from django.db import models

class Court(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    displayed = models.BooleanField(default=False)
    lat = models.FloatField()
    lon = models.FloatField()
    number = models.IntegerField(null=True)
    areas_of_law = models.ManyToManyField('AreaOfLaw', through='CourtAreasOfLaw', null=True)
    attributes = models.ManyToManyField('CourtAttributeType', through='CourtAttribute', null=True)
    addresses = models.ManyToManyField('AddressType', through='CourtAddress', null=True)
    court_types = models.ManyToManyField('CourtType', through='CourtCourtTypes', null=True)

    def postcodes_covered(self):
        return CourtPostcodes.objects.filter(court=self)

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


class CourtPostcodes(models.Model):
    court = models.ForeignKey(Court)
    postcode = models.CharField(max_length=250)

    def __unicode__(self):
        return "%s covers %s" % (self.court.name, self.postcode)


class AreaOfLaw(models.Model):
    name = models.CharField(max_length=255)

    def __unicode__(self):
        return self.name


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


class CourtAreasOfLaw(models.Model):
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


class ContactType(models.Model):
    name = models.CharField(max_length=255)

    def __unicode__(self):
        return self.name


class CourtContact(models.Model):
    contact_type = models.ForeignKey(ContactType)
    court = models.ForeignKey(Court)
    value = models.CharField(max_length=255)

    def __unicode__(self):
        return "%s for %s is %s" % (self.contact_type.name, self.court.name, self.value)


class CourtType(models.Model):
    name = models.CharField(max_length=255)

    def __unicode__(self):
        return self.name


class CourtCourtTypes(models.Model):
    court = models.ForeignKey(Court)
    court_type = models.ForeignKey(CourtType)

    def __unicode__(self):
        return "Court type for %s is %s" % (self.court.name, self.court_type.name)
