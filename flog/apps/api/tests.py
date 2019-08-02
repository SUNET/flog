
from django.core.cache import cache
from django.test import Client

from flog.apps.event.models import Event, EduroamEvent
from flog.testing import TemporaryDBTestcase

__author__ = 'lundberg'

EVENT_RAW_DATA = """
2013-05-16 12:51:51+00:00;3;https://idp.example.com/idp/shibboleth;https://sp1.example.com/Shibboleth.sso;{}
2013-05-16 12:53:27+00:00;3;https://idp.example.com/idp/shibboleth;https://sp1.example.com/Shibboleth.sso;{}
2013-05-16 14:26:46+00:00;3;https://login,example.com/idp/shibboleth;https://sp2.example.com/Shibboleth.sso;{}
2013-05-16 16:50:02+00:00;3;https://login,example.com/idp/shibboleth;https://sp2.example.com/Shibboleth.sso;{}
2013-05-16 19:41:25+00:00;3;https://login,example.com/shibboleth;https://sp2.example.com/Shibboleth.sso;{}
2013-05-17 00:01:16+00:00;3;https://proxy,example.com/idp/shibboleth;https://sp3.example.com/Shibboleth.sso;{}
2013-05-17 00:01:38+00:00;3;https://proxy,example.com/idp/shibboleth;https://sp3.example.com/Shibboleth.sso;{}
2013-05-17 00:10:29+00:00;3;https://proxy,example.com/idp/shibboleth;https://sp3.example.com/Shibboleth.sso;{}
2013-05-17 00:19:48+00:00;3;https://user.example.com/idp/shibboleth;https://sp3.example.com/Shibboleth.sso;{}
2013-05-17 07:12:32+00:00;3;https://user.example.com/idp/shibboleth;https://sp4.example.com/aws-sp;{}
""".format(*[TemporaryDBTestcase.random_string('pn') for _ in range(10)])

EDUROAM_EVENT_RAW_DATA = """
2013-09-09 14:59:51+00:00;eduroam;1.0;example.se;se;example.com;{};OK
2013-09-09 14:59:54+00:00;eduroam;1.0;example.se;se;example.com;{};OK
2013-09-09 15:00:35+00:00;eduroam;1.0;example.se;se;example.com;{};OK
2013-09-09 15:00:35+00:00;eduroam;1.0;example.se;se;example.org;{};OK
2013-09-09 15:00:53+00:00;eduroam;1.0;example.fi;fi;example.org;{};OK
2013-09-09 15:00:56+00:00;eduroam;1.0;example.fi;fi;example.org;{};OK
2013-09-09 15:02:08+00:00;eduroam;1.0;example.fi;fi;example.net;{};OK
2013-09-09 15:02:33+00:00;eduroam;1.0;example.dk;dk;example.net;{};OK
2013-09-09 15:03:25+00:00;eduroam;1.0;example.dk;dk;example.net;{};OK
2013-09-09 15:03:27+00:00;eduroam;1.0;example.dk;dk;example.net;{};OK
""".format(*[TemporaryDBTestcase.random_string('csi') for _ in range(10)])


class ImportTests(TemporaryDBTestcase):

    @classmethod
    def setUpClass(cls):
        super(ImportTests, cls).setUpClass()

    @classmethod
    def setUpTestData(cls):
        # Set up data for the whole TestCase
        pass

    def setUp(self):
        super(ImportTests, self).setUp()
        self.client = Client()

    @classmethod
    def tearDownClass(cls):
        super(ImportTests, cls).tearDownClass()

    def test_import_websso(self):
        resp = self.client.get('/api/import')
        self.assertEqual(resp.status_code, 400)
        self.client.generic('POST', '/api/import', EVENT_RAW_DATA)
        self.assertEqual(Event.objects.count(), 10)

    def test_import_eduroam(self):
        resp = self.client.get('/api/import')
        self.assertEqual(resp.status_code, 400)
        self.client.generic('POST', '/api/import', EDUROAM_EVENT_RAW_DATA)
        self.assertEqual(EduroamEvent.objects.count(), 10)
