from django.conf import settings

from moj_irat.healthchecks import UrlHealthcheck, registry

registry.register_healthcheck(UrlHealthcheck(
    name='mapit',
    url='%sSW1A+1AA' % settings.MAPIT_BASE_URL,
    value_at_json_path=('SW1A 1AA', 'postcode'),
    headers={'X-Api-Key': settings.MAPTI_API_KEY}
))
