# -*- coding: utf-8 -*-
import atexit
import logging
import subprocess
import time

import psycopg2
import memcache
from django.test import TestCase

__author__ = 'lundberg'

logger = logging.getLogger(__name__)


class PostgresqlTemporaryInstance(object):
    """
    Singleton to manage a temporary Postgresql instance

    Use this for testing purpose only. The instance is automatically destroyed
    at the end of the program.

    """
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
            atexit.register(cls._instance.shutdown)
        return cls._instance

    def __init__(self):
        self._port = 5432
        logger.debug('Starting temporary postgresql instance on port {}'.format(self._port))

        self._process = subprocess.Popen(['docker', 'run', '--rm',
                                          '-p', '{!s}:5432'.format(self._port),
                                          '-e', 'POSTGRES_PASSWORD=docker',
                                          'docker.sunet.se/library/postgres-9.6:latest',
                                          ],
                                         stdout=open('/tmp/postgres-temp.log', 'wb'),
                                         stderr=subprocess.STDOUT)
        # Wait for the instance to be ready
        for i in range(10):
            time.sleep(1)
            try:
                self._conn = psycopg2.connect(user='postgres', password='docker', host='localhost', port=self._port)
                self._conn.set_session(autocommit=True)
                cur = self._conn.cursor()
                cur.execute('CREATE USER flog;')
                cur.execute('ALTER USER "flog" WITH PASSWORD \'docker\';')
                cur.execute('ALTER USER "flog" CREATEDB;')
                cur.execute('CREATE DATABASE flog;')
                cur.execute('GRANT ALL PRIVILEGES ON DATABASE flog TO flog;')
                cur.close()
                logger.info('Connected to temporary postgres instance: {}'.format(self._conn))
            except psycopg2.OperationalError as e:
                logger.debug('Exception ({})'.format(e))
                logger.debug('Connect failed ({})'.format(i))
                continue
            else:
                if self._conn is not None:
                    break
        else:
            self.shutdown()
            assert False, 'Cannot connect to the postgres instance'

    def close(self):
        if self._conn:
            logger.info('Closing connection {}'.format(self._conn))
            self._conn.close()
            self._conn = None

    def shutdown(self):
        if self._process:
            self.close()
            logger.info('Shutting down {}'.format(self))
            self._process.terminate()
            self._process = None


class MemcachedTemporaryInstance(object):
    """
    Singleton to manage a temporary Memcached instance

    Use this for testing purpose only. The instance is automatically destroyed
    at the end of the program.

    """
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
            atexit.register(cls._instance.shutdown)
        return cls._instance

    def __init__(self):
        self._port = 11211
        logger.debug('Starting temporary memcached instance on port {}'.format(self._port))
        self._process = subprocess.Popen(['docker', 'run', '--rm',
                                          '-p', '{!s}:11211'.format(self._port),
                                          'docker.sunet.se/library/memcached:latest',
                                          ],
                                         stdout=open('/tmp/memcached-temp.log', 'wb'),
                                         stderr=subprocess.STDOUT)
        # Wait for the instance to be ready
        for i in range(100):
            time.sleep(0.2)
            self._conn = memcache.Client(servers='localhost')
            logger.info('Connected to temporary memcached instance: {}'.format(self._conn))
            if self._conn is None:
                continue
            else:
                if self._conn is not None:
                    break
        else:
            self.shutdown()
            assert False, 'Cannot connect to the memcached test instance'

    def close(self):
        if self._conn:
            logger.info('Closing connection {}'.format(self._conn))
            self._conn.disconnect_all()
            self._conn = None

    def shutdown(self):
        if self._process:
            self.close()
            logger.info('Shutting down {}'.format(self))
            self._process.terminate()
            self._process.wait()
            self._process = None


class TemporaryDBTestcase(TestCase):

    tmp_db = PostgresqlTemporaryInstance.get_instance()
    tmp_cache = MemcachedTemporaryInstance.get_instance()

    @classmethod
    def setUpClass(cls):
        super(TemporaryDBTestcase, cls).setUpClass()

    @classmethod
    def setUpTestData(cls):
        # Set up data for the whole TestCase
        pass

    def setUp(self):
        super(TemporaryDBTestcase, self).setUp()
