from django.utils.translation import get_language
from django.conf import settings


def display_court_in_welsh(court_obj):
    return display_in_welsh() and court_obj.welsh_enabled


def display_in_welsh():
    return get_language() == 'cy' and settings.FEATURE_WELSH_ENABLED


def translate_attribute(obj, attribute_name="", welsh=False):
    welsh_attribute_name=attribute_name+"_cy"
    if all([welsh, hasattr(obj, welsh_attribute_name), getattr(obj, welsh_attribute_name)]):
        return getattr(obj, welsh_attribute_name)
    else:
        return getattr(obj, attribute_name)


def translate_type(obj, type_name="", welsh=False, type_field="name"):
    if welsh:
        kwargs = {
            '{0}'.format(type_field): type_name,
        }
        try:
            type_obj = obj.objects.get(**kwargs)
        except obj.DoesNotExist:
            return type_name
        except obj.MultipleObjectsReturned:
            return obj.objects.filter(**kwargs).first()
        welsh_type_field = type_field + "_cy"
        if getattr(type_obj, welsh_type_field):
            return getattr(type_obj, welsh_type_field)
    return type_name