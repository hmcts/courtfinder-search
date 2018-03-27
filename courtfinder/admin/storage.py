import boto3
from django.conf import settings
from django.utils.text import slugify
import logging

from PIL import Image

COURT_IMAGE_SIZE = 600

AWS_ID = settings.AWS_ACCESS_KEY_ID
AWS_KEY = settings.AWS_SECRET_ACCESS_KEY
AWS_BUCKET = settings.APP_S3_BUCKET

IMAGE_ARGS = {'ContentType': 'image/jpeg', 'ACL': 'public-read'}

logger = logging.getLogger(__name__)


class StorageException(Exception):
    pass

def s3():
    return boto3.client('s3',aws_access_key_id=AWS_ID, aws_secret_access_key=AWS_KEY)


def court_image_file_key(court):
    filename = '%s.jpg' % slugify(court.name)
    return filename, 'images/%s' % filename


def upload_court_photo(court, image):
    filename, key = court_image_file_key(court)
    tempfile = '/tmp/%s' % filename

    try:
        im = Image.open(image)
        im.thumbnail((COURT_IMAGE_SIZE, COURT_IMAGE_SIZE), Image.ANTIALIAS)
        im.save(tempfile, format='JPEG')
        s3().upload_file(tempfile, AWS_BUCKET, key, ExtraArgs=IMAGE_ARGS)
        court.image_file = filename
        court.save()
    except Exception as e:
        logger.error(e)
        raise StorageException('Failed to upload image to S3')


def delete_court_photo(court):
    _, key = court_image_file_key(court)
    try:
        s3().delete_object(Bucket=AWS_BUCKET, Key=key)
        court.image_file = None
        court.save()
    except Exception as e:
        logger.error(e)
        raise StorageException('Failed to delete image from S3')
