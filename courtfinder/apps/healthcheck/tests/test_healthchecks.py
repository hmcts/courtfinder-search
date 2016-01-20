import datetime
import hashlib

from django.test import TestCase
from django.utils import timezone

from freezegun import freeze_time
import responses

from moj_irat.healthchecks import registry

from search.models import DataStatus
from healthcheck.healthchecks import CourtDataFreshnessHealthcheck


class CourtDataFreshnessHealthcheckTestCase(TestCase):
    def setUp(self):
        registry.reset()
        self.test_url = 'http://www.example.org/'
        self.healthcheck = CourtDataFreshnessHealthcheck(
            name='test',
            url=self.test_url
        )
        self.ingestion_status = DataStatus.objects.create(
            data_hash="ensure_non_ingestion_tests_dont_break"
        )

    @responses.activate
    def test_response_contains_url(self):
        responses.add(
            responses.GET,
            self.test_url,
            status=200
        )
        response = self.healthcheck()

        self.assertEqual(self.test_url, response.kwargs['url'])

    @responses.activate
    def test_response_contains_md5_of_remote_content(self):
        body_content = '[{}]'
        responses.add(
            responses.GET,
            self.test_url,
            body=body_content,
            status=200
        )
        response = self.healthcheck()

        self.assertEqual(
            hashlib.md5(body_content).hexdigest(),
            response.kwargs['remote_hash']
        )

    @responses.activate
    def test_response_contains_md5_of_local_content(self):
        ingestion_status = DataStatus.objects.create(
            data_hash="wer38hr3hr37hr"
        )
        responses.add(
            responses.GET,
            self.test_url,
            status=200
        )
        response = self.healthcheck()

        self.assertEqual(
            ingestion_status.data_hash,
            response.kwargs['local_hash']
        )

    @responses.activate
    def test_response_contains_date_of_local_content(self):
        ingestion_status = DataStatus.objects.create(
            data_hash="wer38hr3hr37hr"
        )
        responses.add(
            responses.GET,
            self.test_url,
            status=200
        )
        response = self.healthcheck()

        self.assertEqual(
            ingestion_status.last_ingestion_date,
            response.kwargs['local_date']
        )

    @responses.activate
    def test_response_contains_latest_ingestion_status(self):
        new_ingestion_status = DataStatus.objects.create(
            data_hash="newer_ingest"
        )
        responses.add(
            responses.GET,
            self.test_url,
            status=200
        )
        response = self.healthcheck()

        self.assertEqual(
            new_ingestion_status.data_hash,
            response.kwargs['local_hash']
        )
        self.assertEqual(
            new_ingestion_status.last_ingestion_date,
            response.kwargs['local_date']
        )

class CourtDataFreshnessHealthcheckWithStaleDataTestCase(TestCase):
    def setUp(self):
        registry.reset()
        self.test_url = 'http://www.example.org/'
        self.healthcheck = CourtDataFreshnessHealthcheck(
            name='test',
            url=self.test_url
        )

    @responses.activate
    def test_response_errors_if_newer_data_available(self):
        old_ingestion_status = DataStatus.objects.create(
            data_hash="old_ingest"
        )
        responses.add(
            responses.GET,
            self.test_url,
            status=200
        )

        when_old_ingest_becomes_stale = timezone.now() + datetime.timedelta(
            minutes=10, seconds=1
        )
        with freeze_time(when_old_ingest_becomes_stale):
            response = self.healthcheck()

        self.assertFalse(response.status)
        self.assertNotEqual(
            response.kwargs['remote_hash'],
            response.kwargs['local_hash']
        )
        self.assertEqual(
            response.kwargs['error'],
            'Local courts data is different from remote and older than 10min'
        )

    @responses.activate
    def test_response_doesnt_error_with_no_newer_data_available(self):
        body_content = '[{}]'
        old_ingestion_status = DataStatus.objects.create(
            data_hash=hashlib.md5(body_content).hexdigest()
        )
        responses.add(
            responses.GET,
            self.test_url,
            body=body_content,
            status=200
        )

        when_old_ingest_becomes_stale = timezone.now() + datetime.timedelta(
            minutes=10, seconds=1
        )
        with freeze_time(when_old_ingest_becomes_stale):
            response = self.healthcheck()

        self.assertTrue(response.status)
        self.assertEqual(
            response.kwargs['remote_hash'],
            response.kwargs['local_hash']
        )
