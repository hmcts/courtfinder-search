from django.db import models

class Court(models.Model):
  name = models.CharField(max_length=255)
  slug = models.SlugField(max_length=255)
  displayed = models.BooleanField(default=False)
  lat = models.IntegerField()
  lon = models.IntegerField()
  area = models.ForeignKey('Area')
  attributes = models.ManyToManyField('CourtAttributeType', through='CourtAttribute')
  addresses = models.ManyToManyField('AddressType', through='CourtAddress')

  def __unicode__(self):
    return self.name


class Area(models.Model):
  name = models.CharField(max_length=255)

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
    return "%s.%s = %s" % (self.court.name, self.attribute_type.name, value)


class AreaOfLaw(models.Model):
  name = models.CharField(max_length=255)

  def __unicode__(self):
    return self.name


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
  COUNTRIES = [('ENG','England'), ('NIR', 'Northern Ireland'), ('SCT', 'Scotland'), ('WLS', 'Wales')]

  name = models.CharField(max_length=255, choices=COUNTRIES)

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

