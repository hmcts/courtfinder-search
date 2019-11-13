from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.utils.text import slugify
from io import BytesIO
import logging

from PIL import Image

COURT_IMAGE_SIZE = 600
FACILITY_IMAGE_SIZE = 50

IMAGE_ARGS = {'ContentType': 'image/jpeg', 'ACL': 'public-read'}
ICON_ARGS = {'ContentType': 'image/png', 'ACL': 'public-read'}
logger = logging.getLogger(__name__)


class StorageException(Exception):
    pass


def court_image_file_key(court):
    filename = '%s.jpg' % slugify(court.name)
    return filename, 'images/%s' % filename


def upload_court_photo(court, image):
    filename, key = court_image_file_key(court)

    try:
        im = Image.open(image)
        im.thumbnail((COURT_IMAGE_SIZE, COURT_IMAGE_SIZE), Image.ANTIALIAS)

        io = BytesIO()
        im.save(io, format='JPEG')
        resized = ContentFile(io.getvalue())

        default_storage.save(key, resized)

        court.image_file = filename
        court.save()
    except Exception as e:
        logger.error(e)
        raise StorageException('Failed to upload image to storage')


def delete_court_photo(court):
    _, key = court_image_file_key(court)
    try:
        default_storage.delete(key)
        court.image_file = None
        court.save()
    except Exception as e:
        logger.error(e)
        raise StorageException('Failed to delete image from storage')


def facility_image_file_path(facility_type):
    filename = '%s.png' % slugify(facility_type.name)
    if facility_type.image_file_path:
        return facility_type.image_file_path
    return 'uploads/facility/%s' % filename


def upload_facility_icon(facility_type, image):
    filename = facility_image_file_path(facility_type)

    try:
        im = Image.open(image)
        im.thumbnail((FACILITY_IMAGE_SIZE, FACILITY_IMAGE_SIZE), Image.ANTIALIAS)

        io = BytesIO()
        im.save(io, format='PNG')
        resized = ContentFile(io.getvalue())

        default_storage.save(filename, resized)

        facility_type.image_file_path = filename
        facility_type.save()
    except Exception as e:
        logger.error(e)
        raise StorageException('Failed to upload image to storage')
