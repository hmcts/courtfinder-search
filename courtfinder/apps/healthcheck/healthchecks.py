import datetime
import hashlib

from django.conf import settings
from django.utils import timezone

from moj_irat.healthchecks import \
    HealthcheckResponse, \
    UrlHealthcheck, \
    registry

from search.models import DataStatus


class CourtDataFreshnessHealthcheck(UrlHealthcheck):
    """Healthcheck for freshness of court data"""

    def success_response(self, url_response):
        response = super(
            CourtDataFreshnessHealthcheck,
            self
        ).success_response(url_response)

        if response.status:
            digest = hashlib.md5()
            for chunk in url_response.iter_content(1024):
                digest.update(chunk)

            response.kwargs['remote_hash'] = digest.hexdigest()

            last_ingestion = DataStatus.objects.all().order_by(
                '-last_ingestion_date'
            ).first()
            response.kwargs['local_hash'] = last_ingestion.data_hash
            response.kwargs['local_date'] = last_ingestion.last_ingestion_date

            ten_minutes_ago = timezone.now() - datetime.timedelta(minutes=10)
            if response.kwargs['local_hash'] != response.kwargs['remote_hash'] \
                and last_ingestion.last_ingestion_date < ten_minutes_ago:
                response.status = False
                response.kwargs['error'] = 'Local courts data is different ' \
                    'from remote and older than 10min'

        return response


registry.register_healthcheck(UrlHealthcheck(
    name='mapit',
    url='%sSW1A+1AA' % settings.MAPIT_BASE_URL,
    value_at_json_path=('SW1A 1AA', 'postcode'),
))
registry.register_healthcheck(UrlHealthcheck(
    name='courtfinder_admin',
    url=settings.COURTFINDER_ADMIN_HEALTHCHECK_URL,
))
registry.register_healthcheck(CourtDataFreshnessHealthcheck(
    name='courts_data',
    url=settings.COURTS_DATA_S3_URL,
))
