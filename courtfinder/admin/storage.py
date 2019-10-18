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


def court_image_file(court):
    filename = '%s.jpg' % slugify(court.name)
    return 'court/%s' % filename


def upload_court_photo(court, image):
    path = court_image_file(court)

    try:
        im = Image.open(image)
        im.thumbnail((COURT_IMAGE_SIZE, COURT_IMAGE_SIZE), Image.ANTIALIAS)

        io = BytesIO()
        im.save(io, format='JPEG')
        resized = ContentFile(io.getvalue())

        default_storage.save(path, resized)
        court.image_file = path
        court.save()
    except Exception as e:
        logger.error(e)
        raise StorageException('Failed to upload image to storage')


def delete_court_photo(court):
    path = court_image_file(court)
    try:
        default_storage.delete(path)
        court.image_file = None
        court.save()
    except Exception as e:
        logger.error(e)
        raise StorageException('Failed to delete image from storage')


def upload_facility_icon(facility_type, image):
    filename = '%s.png' % slugify(facility_type.name)
    path = 'facility/%s' % filename

    try:
        im = Image.open(image)
        im.thumbnail((FACILITY_IMAGE_SIZE, FACILITY_IMAGE_SIZE), Image.ANTIALIAS)

        io = BytesIO()
        im.save(io, format='PNG')
        resized = ContentFile(io.getvalue())

        default_storage.save(path, resized)

        facility_type.image_file_path = path
        facility_type.save()
    except Exception as e:
        logger.error(e)
        raise StorageException('Failed to upload image to storage')
