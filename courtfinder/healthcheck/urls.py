from django.conf.urls import url

from moj_irat.views import HealthcheckView, PingJsonView

app_name='healthcheck'
urlpatterns = [
    url(r'^ping.json$', PingJsonView.as_view(
        build_date_key='APP_BUILD_DATE',
        commit_id_key='APP_GIT_COMMIT',
        build_tag_key='APP_BUILD_TAG',
        version_number_key='APP_VERSION',
    ), name='ping_json'),
    url(r'^healthcheck.json$',
        HealthcheckView.as_view(),
        name='healthcheck_json'
    ),
]
