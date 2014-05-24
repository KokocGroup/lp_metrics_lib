# -*- coding: utf-8 -*-

from redis import StrictRedis
try:
    from django.conf import settings
except ImportError:
    import settings

REDIS_METRICS_HOST = getattr(settings, 'REDIS_METRICS_HOST', 'localhost')
REDIS_METRICS_PORT = getattr(settings, 'REDIS_METRICS_PORT', 6379)
REDIS_METRICS_PASSWORD = getattr(settings, 'REDIS_METRICS_PASSWORD', None)
REDIS_METRICS_DB = getattr(settings, 'REDIS_METRICS_DB', 5)

REDIS_METRICS_READ_HOST = getattr(
    settings, 'REDIS_METRICS_READ_HOST', 'localhost')
REDIS_METRICS_READ_PORT = getattr(settings, 'REDIS_METRICS_READ_PORT', 6379)
REDIS_METRICS_READ_PASSWORD = getattr(
    settings, 'REDIS_METRICS_READ_PASSWORD', None)
REDIS_METRICS_READ_DB = getattr(settings, 'REDIS_METRICS_READ_DB', 5)

REDIS_SESSION_HOST = getattr(settings, 'REDIS_SESSION_HOST', 'localhost')
REDIS_SESSION_PORT = getattr(settings, 'REDIS_SESSION_PORT', 6379)
REDIS_SESSION_PASSWORD = getattr(settings, 'REDIS_SESSION_PASSWORD', None)
REDIS_SESSION_DB = getattr(settings, 'REDIS_SESSION_DB', 6)


class RedisMetricsClient(StrictRedis):
    def __init__(self):
        super(RedisMetricsClient, self).__init__(
            host=REDIS_METRICS_HOST, port=REDIS_METRICS_PORT,
            db=REDIS_METRICS_DB, password=REDIS_METRICS_PASSWORD)


class RedisMetricsClientRead(StrictRedis):
    def __init__(self):
        super(RedisMetricsClientRead, self).__init__(
            host=REDIS_METRICS_READ_HOST, port=REDIS_METRICS_READ_PORT,
            db=REDIS_METRICS_READ_DB, password=REDIS_METRICS_READ_PASSWORD)


class RedisSessionClient(StrictRedis):
    def __init__(self):
        super(RedisSessionClient, self).__init__(
            host=REDIS_SESSION_HOST, port=REDIS_SESSION_PORT,
            db=REDIS_SESSION_DB, password=REDIS_SESSION_PASSWORD)
