from django.conf.urls import patterns, url

from moj_irat.views import PingJsonView

urlpatterns = patterns('healthcheck.views',
    url(r'^ping.json$', PingJsonView.as_view(
        build_date_key='APP_BUILD_DATE',
        commit_id_key='APP_GIT_COMMIT',
        build_tag_key='APP_BUILD_TAG',
        version_number_key='APP_VERSION',
    ), name='ping_json'),
    url(r'^healthcheck.json$', 'healthcheck'),
    url(r'^pingdom-search-statistics$', 'pingdom_search_statistics'),
)
