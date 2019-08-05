"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
from datetime import datetime, timedelta

from dateutil import tz
from django.test.client import Client
from django.core.management import call_command
from six import StringIO
from operator import itemgetter

from flog.apps.event import models
from flog.testing import TemporaryDBTestcase


def format_datetime_str(dt):
    dt = dt.replace(tzinfo=tz.tzutc())
    return dt.strftime('%Y-%m-%d %H:%M:%S %Z')


class TestEvent(TemporaryDBTestcase):

    @classmethod
    def setUpTestData(cls):
        # Set up data for the whole TestCase
        cls.idp = models.Entity.objects.create(uri='https://idp.example.com', is_idp=True)
        cls.sp = models.Entity.objects.create(uri='https://sp.example.com', is_rp=True)
        cls.event = models.Event.objects.create(ts=datetime.utcnow(), origin=cls.idp, rp=cls.sp,
                                                protocol=models.Event.SAML2, principal=TestEvent.random_string('pn'))

    def setUp(self):
        self.client = Client()

    def test_index(self):
        resp = self.client.get('/')
        self.assertContains(resp, 'SWAMID Statistics')

    def test_websso_list(self):
        resp = self.client.get('/event/websso/')
        self.assertTemplateNotUsed('event/websso_list.html')
        self.assertEqual(len(resp.context['rps']), 1)
        self.assertEqual(len(resp.context['idps']), 1)
        self.assertEqual(resp.context['rps'][0].uri, 'https://sp.example.com')
        self.assertEqual(resp.context['idps'][0].uri, 'https://idp.example.com')

    def test_websso_get_rp_detail(self):
        resp = self.client.get('/event/websso/rp/{}/'.format(self.sp.pk))
        self.assertTemplateNotUsed('event/piechart.html')
        self.assertEqual(resp.context['entity'], self.sp)
        self.assertEqual(resp.context['default_min'], 15)
        self.assertEqual(resp.context['default_max'], 1)

    def test_websso_post_rp_detail(self):
        start_dt = datetime.utcnow() - timedelta(days=1)
        data = {'start': format_datetime_str(start_dt), 'end': format_datetime_str(datetime.utcnow()),
                'protocol': 3}
        resp = self.client.post('/event/websso/rp/{}/'.format(self.sp.pk), data=data)
        self.assertEqual(resp.json()[0]['data'], 1)
        self.assertEqual(resp.json()[0]['id'], self.idp.pk)
        self.assertEqual(resp.json()[0]['label'], 'https://idp.example.com')

    def test_websso_get_origin_detail(self):
        resp = self.client.get('/event/websso/origin/{}/'.format(self.idp.pk))
        self.assertTemplateNotUsed('event/piechart.html')
        self.assertEqual(resp.context['entity'], self.idp)
        self.assertEqual(resp.context['default_min'], 15)
        self.assertEqual(resp.context['default_max'], 1)

    def test_websso_post_origin_detail(self):
        start_dt = datetime.utcnow() - timedelta(days=1)
        data = {'start': format_datetime_str(start_dt), 'end': format_datetime_str(datetime.utcnow()),
                'protocol': 3}
        resp = self.client.post('/event/websso/origin/{}/'.format(self.idp.pk), data=data)
        self.assertEqual(resp.json()[0]['data'], 1)
        self.assertEqual(resp.json()[0]['id'], self.sp.pk)
        self.assertEqual(resp.json()[0]['label'], 'https://sp.example.com')

    def test_get_websso_auth_flow(self):
        # Run management commond to aggregate event
        out = StringIO()
        call_command('aggregate_events_daily', 'all', stdout=out)

        resp = self.client.get('/event/websso/authentication-flow/')
        self.assertTemplateNotUsed('event/sankey.html')
        self.assertEqual(resp.context['default_min'], 1)
        self.assertEqual(resp.context['default_max'], 1)

    def test_post_websso_auth_flow(self):
        # Run management commond to aggregate event
        out = StringIO()
        call_command('aggregate_events_daily', 'all', stdout=out)

        start_dt = datetime.utcnow() - timedelta(days=1)
        data = {'start': format_datetime_str(start_dt), 'end': format_datetime_str(datetime.utcnow()),
                'protocol': 3}
        resp = self.client.post('/event/websso/authentication-flow/', data=data)
        self.assertEqual(len(resp.json()['nodes']), 2)
        self.assertEqual(len(resp.json()['links']), 1)
        self.assertEqual(resp.json()['links'][0]['value'], 1)


class TestEduroamEvent(TemporaryDBTestcase):

    @classmethod
    def setUpTestData(cls):
        # Set up data for the whole TestCase
        cls.country1 = models.Country.objects.create(country_code='se', name='Sweden')
        cls.country2 = models.Country.objects.create(country_code='dk', name='Denmark')
        cls.realm1 = models.EduroamRealm.objects.create(realm='example.se', country=cls.country1, name='Realm1')
        cls.realm2 = models.EduroamRealm.objects.create(realm='example.dk', country=cls.country2, name='Realm2')
        cls.event1 = models.EduroamEvent.objects.create(ts=datetime.utcnow(), version=1, realm=cls.realm1,
                                                        visited_country=cls.country2, visited_institution=cls.realm2,
                                                        calling_station_id=cls.random_string('csi'), successful=True)
        cls.event2 = models.EduroamEvent.objects.create(ts=datetime.utcnow()+timedelta(seconds=600), version=1,
                                                        realm=cls.realm1, visited_country=cls.country1,
                                                        visited_institution=cls.realm1,
                                                        calling_station_id=cls.random_string('csi'), successful=True)

    def setUp(self):
        self.client = Client()

    def test_index(self):
        resp = self.client.get('/')
        self.assertContains(resp, 'SWAMID Statistics')

    def test_eduroam_list(self):
        resp = self.client.get('/event/eduroam/')
        self.assertTemplateNotUsed('event/eduroam_list.html')
        self.assertEqual(len(resp.context['countries']), 2)

    def test_eduroam_get_realm_list(self):
        # Run management commond to aggregate eduroam event
        out = StringIO()
        call_command('aggregate_eduroam_events_daily', 'all', stdout=out)

        resp = self.client.get('/event/eduroam/{}/'.format(self.country1.country_code))
        self.assertTemplateNotUsed('event/eduroam_list.html')
        self.assertEqual(resp.context['country_name'], self.country1.name)
        self.assertEqual(len(resp.context['to_country']), 1)
        self.assertEqual(len(resp.context['from_country']), 1)

    def test_eduroam_ge_to_realm(self):
        # Run management commond to aggregate eduroam event
        out = StringIO()
        call_command('aggregate_eduroam_events_daily', 'all', stdout=out)

        resp = self.client.get('/event/eduroam/to/{}/'.format(self.realm2.pk))
        self.assertTemplateNotUsed('event/eduroam_list.html')
        self.assertEqual(resp.context['realm'], self.realm2)
        self.assertEqual(resp.context['cross_type'], 'from')
        self.assertEqual(resp.context['threshold'], 0.01)
        self.assertEqual(resp.context['default_max'], 1)
        self.assertEqual(resp.context['default_min'], 15)

    def test_eduroam_get_from_realm(self):
        # Run management commond to aggregate eduroam event
        out = StringIO()
        call_command('aggregate_eduroam_events_daily', 'all', stdout=out)

        resp = self.client.get('/event/eduroam/from/{}/'.format(self.realm1.pk))
        self.assertTemplateNotUsed('event/eduroam_list.html')
        self.assertEqual(resp.context['realm'], self.realm1)
        self.assertEqual(resp.context['cross_type'], 'to')
        self.assertEqual(resp.context['threshold'], 0.01)
        self.assertEqual(resp.context['default_max'], 1)
        self.assertEqual(resp.context['default_min'], 15)

    def test_get_eduroam_auth_flow(self):
        # Run management commond to aggregate event
        out = StringIO()
        call_command('aggregate_eduroam_events_daily', 'all', stdout=out)

        resp = self.client.get('/event/eduroam/authentication-flow/')
        self.assertTemplateNotUsed('event/sankey.html')
        self.assertEqual(resp.context['default_min'], 1)
        self.assertEqual(resp.context['default_max'], 1)

    def test_post_eduroam_auth_flow(self):
        # Run management commond to aggregate event
        out = StringIO()
        call_command('aggregate_eduroam_events_daily', 'all', stdout=out)

        start_dt = datetime.utcnow() - timedelta(days=1)
        data = {'start': format_datetime_str(start_dt), 'end': format_datetime_str(datetime.utcnow()),
                'protocol': 'eduroam'}
        resp = self.client.post('/event/eduroam/authentication-flow/', data=data)
        self.assertEqual(sorted(resp.json()['nodes'], key=itemgetter('id')),
                         sorted([
                             {u'id': u'from-Sweden', u'name': u'Sweden'},
                             {u'id': u'to-Sweden', u'name': u'Sweden'},
                             {u'id': u'from-example.se', u'name': u'example.se'},
                             {u'id': u'to-example.se', u'name': u'example.se'},
                             {u'id': u'to-Denmark', u'name': u'Denmark'}
                         ], key=itemgetter('id')))
        self.assertEqual(sorted(resp.json()['links'], key=itemgetter('source', 'target')),
                         sorted([
                             {u'source': u'from-example.se', u'target': u'to-Denmark', u'value': 1},
                             {u'source': u'to-example.se', u'target': u'to-Sweden', u'value': 1},
                             {u'source': u'from-example.se', u'target': u'to-example.se', u'value': 1},
                             {u'source': u'to-Denmark', u'target': u'to-Denmark', u'value': 1},
                             {u'source': u'from-Sweden', u'target': u'from-example.se', u'value': 2}
                         ], key=itemgetter('source', 'target')))
