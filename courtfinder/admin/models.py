from django.db import models


class FacilityType(models.Model):
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=4096, null=True, blank=True)
    image = models.CharField(max_length=255)
    image_description = models.CharField(max_length=255)
    image_file_path = models.CharField(max_length=255, null=True, blank=True)
    order = models.IntegerField(null=False, default=0)

    def __unicode__(self):
        return self.name

    @property
    def order_label(self):
        return "%s" % self.name


class ContactType(models.Model):
    name = models.CharField(max_length=255)

    def __unicode__(self):
        return self.name


class OpeningType(models.Model):
    name = models.CharField(max_length=255)

    def __unicode__(self):
        return self.name