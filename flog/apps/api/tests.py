
from django.core.cache import cache
from flog.testing import TemporaryDBTestcase

__author__ = 'lundberg'

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

    @classmethod
    def tearDownClass(cls):
        super(ImportTests, cls).tearDownClass()

    def test1(self):
        print(self.tmp_db)

    def test2(self):
        cache.set('test', 123)
        print(cache.get('test'))

