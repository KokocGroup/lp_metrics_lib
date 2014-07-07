# -*- coding: utf-8 -*-

__author__ = 'gotlium'
__version__ = '1.0.1'

from json import dumps, loads
from datetime import datetime, timedelta

from time import time
from pytz import utc

from metrics.redis_wrapper import RedisMetricsClient


ADDITIONAL_STRUCT = ('id', 'type', 'label', 'count')


def now():
    return datetime.utcnow().replace(tzinfo=utc)


class MetricsAbstract(object):
    """
    Basic abstract class, for store counters into redis
    """
    variants_key = 'variants'
    namespace = 'metrics'

    def __init__(self, variant_id, date_string, redis, save_variant=True):
        self.variant_id = variant_id
        self.date_string = date_string
        self.save_variant = save_variant

        self.redis = redis
        self._save_variants()

    def __get_variants_key(self):
        """
        Get variants ids which stored to specified date
        """
        return '%s:%s:%s' % (
            self.namespace, self.date_string, self.variants_key)

    def _save_variants(self):
        """
        For every call, variant will be stored.
        That need for sync data with database, without scanning by all variants
        """
        if self.variant_id and self.save_variant:
            self.redis.hset(self.__get_variants_key(), self.variant_id, '')

    def _get_redis_key(self, args):
        """
        Get key with specified namespace, date & variant.
        Key can be mixed with some tuples
        """
        keys = [self.namespace, self.date_string, self.variant_id]
        keys.extend(args)
        return ':'.join(map(str, keys))

    def _del_by(self, key):
        """
        Delete data by specified key
        """
        self.redis.delete(self._get_redis_key(key))

    def _hash_increment_by(self, hash_key, key):
        return self.redis.hincrby(self._get_redis_key(hash_key), key, 1)

    def _hash_get_by(self, key):
        return self.redis.hgetall(self._get_redis_key(key))

    def _get_hash_key(self, *args):
        return ':'.join(map(str, args))

    def _increment_by(self, key, amount=1):
        """
        Incrementing value by specified key
        """
        return self.redis.incrby(self._get_redis_key(key), amount)

    def _get_count_by(self, key):
        """
        Get incremented value by specified key
        """
        return self.redis.get(self._get_redis_key(key)) or 0

    def clean_up(self):
        """
        Abstract method for implementation on child classes
        """
        raise NotImplementedError()

    def flush_db(self):
        """
        Remove all data for defined date
        """
        keys_list = self.redis.keys('%s:%s:*' % (
            self.namespace, self.date_string))
        for key in keys_list:
            self.redis.delete(key)

    def get_variants(self):
        """
        Get all page variants, which was saved for defined date
        """
        return self.redis.hkeys(self.__get_variants_key())

    def _get_counter_key(self, t, value):
        """
        Get value by specified key converted into dictionary
        """
        k = {
            '0': 'visits',
            '1': 'unique',
            '2': 'goals',
            '3': 'leads',
        }.get(t)
        return {k: value}


class VisitorMetrics(MetricsAbstract):
    visits_key = ('count', 0,)
    unique_key = ('count', 1,)
    goals_key = ('count', 2,)
    geo_goals_key = ('count_geo_goals',)
    geo_unique_key = ('count_geo_unique',)
    details_key = ('count_details',)
    additional_key = ('count_additional',)

    def get_unique(self):
        return self._get_count_by(self.unique_key)

    def get_visits(self):
        return self._get_count_by(self.visits_key)

    def get_goals(self):
        return self._get_count_by(self.goals_key)

    def get_additional_list(self):
        data = []
        ad_list = self.redis.hgetall(self._get_redis_key(self.additional_key))
        for key, count in ad_list.items():
            values = key.split(':') + [count]
            data.append(dict(zip(ADDITIONAL_STRUCT, values)))
        return data

    def get_details(self):
        data = self.redis.lrange(self._get_redis_key(self.details_key), 0, -1)
        keys = ['ip', 'time', 'channel']
        for line in data:
            yield dict(zip(keys, loads(line)))

    def get_geo(self):
        keys = self.redis.hgetall(self._get_redis_key(self.geo_unique_key))
        data = []
        for ip, unique in keys.items():
            goals = self.redis.hget(
                self._get_redis_key(self.geo_goals_key), ip)
            data.append({
                'ip': ip,
                'unique': int(unique or 0),
                'goals': int(goals or 0),
            })
        return data

    def _save_details(self, data):
        self.redis.lpush(
            self._get_redis_key(self.details_key), dumps(data))

    def _save_geo(self, data, is_goal=0):
        if not is_goal:
            self.redis.hincrby(
                self._get_redis_key(self.geo_unique_key), data[0], 1)
        self.redis.hincrby(
            self._get_redis_key(self.geo_goals_key), data[0], is_goal)

    def save_visitor(self, is_unique, data):
        if is_unique > 0:
            self._increment_by(self.unique_key)
            self._save_details(data)
            self._save_geo(data)
        self._increment_by(self.visits_key)

    def save_goal(self, data):
        self._increment_by(self.goals_key)
        self._save_geo(data, is_goal=1)

    def save_additional(self, **kwargs):
        if kwargs.get('ad_id') and kwargs.get('ad_type'):
            key = '%(ad_id)s:%(ad_type)s:%(ad_label)s' % kwargs
            self.redis.hincrby(self._get_redis_key(self.additional_key), key)

    def clean_up(self):
        self._del_by(self.visits_key)
        self._del_by(self.unique_key)
        self._del_by(self.goals_key)
        self._del_by(self.details_key)
        self._del_by(self.additional_key)
        self._del_by(self.geo_goals_key)
        self._del_by(self.geo_unique_key)


class UtmMetrics(MetricsAbstract):
    utm_channel_key = ('utm_source',)
    utm_medium_key = ('utm_medium',)
    utm_campaign_key = ('utm_campaign',)
    utm_term_key = ('utm_term',)
    utm_additional_keys_key = ('utm_additional_keys',)
    utm_additional_key = ('utm_additional',)

    def __init__(self, *args, **kwargs):
        super(UtmMetrics, self).__init__(*args, **kwargs)

        self.channel_id = None
        self.utm_params = None
        self.count_type = None
        self.additional_params = None

        self.utm_medium = None
        self.utm_campaign = None

        self.data = dict()

    def __get_additional_name(self, name):
        return self._get_redis_key([self.utm_additional_keys_key[0], name])

    def _save_utm_additional(self, name):
        params = self.additional_params
        if params and params.get('ad_id') and params.get('ad_type'):
            if self.count_type == 2:
                key = name + '-||-%(ad_id)s:%(ad_type)s:%(ad_label)s' % params
                self.redis.sadd(self.__get_additional_name(name), key)
                self._hash_increment_by(self.utm_additional_key, key)

    def _get_utm_additional(self, name):
        data = []
        for key in self.redis.smembers(self.__get_additional_name(name)):
            cnt_key = self._get_redis_key(self.utm_additional_key)
            count = [self.redis.hget(cnt_key, key)]
            values = key.split('-||-')[1].split(':') + count
            data.append(dict(zip(ADDITIONAL_STRUCT, values)))
        return {'additional': data}

    def _del_utm_additional(self):
        for key in self.redis.keys(self.__get_additional_name('*')):
            self.redis.delete(key)

    def _save_utm_term(self):
        utm_terms = self.utm_params.get('utm_term')
        if utm_terms:
            for term in utm_terms.split(','):
                term = term.strip()
                if term:
                    key = self._get_hash_key(
                        term, self.utm_campaign, self.utm_medium,
                        self.channel_id, self.count_type)
                    self._hash_increment_by(self.utm_term_key, key)
                    self._save_utm_additional(key)

    def _save_utm_campaign(self):
        self.utm_campaign = self.utm_params.get('utm_campaign')
        if self.utm_campaign:
            key = self._get_hash_key(
                self.utm_campaign, self.utm_medium,
                self.channel_id, self.count_type)
            self._save_utm_additional(key)
            return self._hash_increment_by(self.utm_campaign_key, key)

    def _save_utm_medium(self):
        self.utm_medium = self.utm_params.get('utm_medium')
        if self.utm_medium:
            key = self._get_hash_key(
                self.utm_medium, self.channel_id, self.count_type)
            self._save_utm_additional(key)
            return self._hash_increment_by(self.utm_medium_key, key)

    def _save_channel(self):
        key = self._get_hash_key(self.channel_id, self.count_type)
        self._save_utm_additional(key)
        return self._hash_increment_by(self.utm_channel_key, key)

    def _get_utm_terms(self):
        utm_terms = self._hash_get_by(self.utm_term_key)
        for term_key, term_count in utm_terms.items():
            term, campaign, medium, channel, count_type = term_key.split(':')
            if term not in self.data[channel]['utm_medium'][medium]['utm_campaign'][campaign]['terms']:
                self.data[channel]['utm_medium'][medium]['utm_campaign'][campaign]['terms'][term] = {}

            self.data[channel]['utm_medium'][medium]['utm_campaign'][campaign]['terms'][term].update(
                self._get_counter_key(count_type, term_count))

            if count_type == '2':
                self.data[channel]['utm_medium'][medium]['utm_campaign'][campaign]['terms'][term].update(
                    self._get_utm_additional(term_key))

    def _get_utm_campaign(self):
        utm_campaign = self._hash_get_by(self.utm_campaign_key)
        for campaign_key, campaign_count in utm_campaign.items():
            campaign, medium, channel, count_type = campaign_key.split(':')

            if campaign not in self.data[channel]['utm_medium'][medium]['utm_campaign']:
                self.data[channel]['utm_medium'][medium]['utm_campaign'][campaign] = {'terms': {}}

            self.data[channel]['utm_medium'][medium]['utm_campaign'][campaign].update(
                self._get_counter_key(count_type, campaign_count))

            if count_type == '2':
                self.data[channel]['utm_medium'][medium]['utm_campaign'][campaign].update(
                    self._get_utm_additional(campaign_key))

    def _get_utm_medium(self):
        utm_medium = self._hash_get_by(self.utm_medium_key)
        for medium_key, medium_count in utm_medium.items():
            medium, channel, count_type = medium_key.split(':')
            if medium not in self.data[channel]['utm_medium']:
                self.data[channel]['utm_medium'][medium] = {'utm_campaign': {}}

            self.data[channel]['utm_medium'][medium].update(
                self._get_counter_key(count_type, medium_count))

            if count_type == '2':
                self.data[channel]['utm_medium'][medium].update(
                    self._get_utm_additional(medium_key))

    def _get_utm_channel(self):
        utm_channel = self._hash_get_by(self.utm_channel_key)

        for channel_data, channel_count in utm_channel.items():
            channel, channel_type = channel_data.split(':')

            if channel not in self.data:
                self.data[channel] = {'utm_medium': {}}

            self.data[channel].update(self._get_counter_key(
                channel_type, channel_count))

            if channel_type == '2':
                self.data[channel].update(
                    self._get_utm_additional(channel_data))

    def _save_utm(self):
        if self.variant_id and self.channel_id:
            if self._save_channel():
                if self._save_utm_medium():
                    if self._save_utm_campaign():
                        self._save_utm_term()

    def _encode_params(self):
        for k, v in self.utm_params.items():
            if v is not None:
                try:
                    self.utm_params[k] = v.encode('utf-8', 'ignore')
                except UnicodeDecodeError:
                    self.utm_params[k] = v

    def clean_up(self):
        self._del_by(self.utm_channel_key)
        self._del_by(self.utm_medium_key)
        self._del_by(self.utm_campaign_key)
        self._del_by(self.utm_term_key)
        self._del_by(self.utm_additional_key)
        self._del_utm_additional()

    def get_utm(self):
        self._get_utm_channel()
        self._get_utm_medium()
        self._get_utm_campaign()
        self._get_utm_terms()
        return self.data

    def save_utm(self, channel_id, utm_params,
                 additional_params, count_type=0):
        self.channel_id = channel_id
        self.utm_params = utm_params
        self.count_type = count_type
        self.additional_params = additional_params

        self._encode_params()
        self._save_utm()

    def save_visit_with_utm(self, is_unique, channel_id=None, utm_params=None):
        if is_unique:
            self.save_utm(channel_id, utm_params, None, 1)
        self.save_utm(channel_id, utm_params, None, 0)

    def save_utm_goal(self, channel_id, utm_params, additional_params):
        self.save_utm(channel_id, utm_params, additional_params, 2)


class HourMetrics(MetricsAbstract):
    hour_key = ('hour_statistics',)
    namespace = 'hours'

    def __init__(self, variant_id, date_string, redis, save_variant=True):
        super(HourMetrics, self).__init__(
            variant_id, date_string, redis, save_variant)

        self.time_string = now().strftime('%H')

    def clean_up(self):
        self._del_by(self.hour_key)

    def _save_by_key(self, type_key):
        key = self._get_hash_key(self.time_string, type_key)
        return self._hash_increment_by(self.hour_key, key)

    def _save_visitor(self, is_unique=0):
        self._save_by_key(is_unique)

    def save_visitor(self, is_unique=0):
        if is_unique:
            self._save_visitor(1)
        self._save_visitor()

    def save_goal(self):
        return self._save_by_key(2)

    def save_lead(self):
        return self._save_by_key(3)

    def get_hours_stats(self):
        data_list = self.redis.hgetall(self._get_redis_key(self.hour_key))
        hours_stats = {}
        for data, count in data_list.items():
            hour, count_type = data.split(':')
            if hour not in hours_stats:
                hours_stats[hour] = {}
            hours_stats[hour].update(self._get_counter_key(count_type, count))
        return hours_stats


class TariffStats(MetricsAbstract):
    """
    Class for track only unique visits for current month
    """
    variants_key = 'profiles'
    namespace = 'stats'
    tariff_key = ('tariff',)

    def save_unique(self):
        return self._increment_by(self.tariff_key)

    def get_unique(self):
        return self._get_count_by(self.tariff_key)

    def clean_up(self):
        previous_mon = (now() - timedelta(days=31)).strftime('%Y-%m')
        self.date_string = previous_mon
        for profile in self.get_variants():
            self.variant_id = profile
            key = self._get_redis_key(self.tariff_key)
            self.redis.delete(key)


class TotalMetrics(MetricsAbstract):
    """
    Class for save total counters for page to view on /pages/
    """
    namespace = 'total_metrics'

    conversion_key = ('count', 0,)
    unique_key = ('count', 1,)
    goals_key = ('count', 2,)
    details_key = ('count_details',)

    def __init__(self, page_id, redis, save_variant=True):
        super(TotalMetrics, self).__init__(
            page_id, '0000-00-00', redis, save_variant)

    def get_unique(self):
        return self._get_count_by(self.unique_key)

    def get_conversions(self):
        pipe = self.redis.pipeline(transaction=True)
        pipe.get(self._get_redis_key(self.goals_key))
        pipe.get(self._get_redis_key(self.unique_key))
        data = pipe.execute()
        goals = float(data[0] or 0)
        unique = float(data[1] or 0)
        try:
            conversions = goals / unique * 100.0
        except ZeroDivisionError:
            conversions = 0.0
        return '%0.2f' % conversions

    def get_goals(self):
        return self._get_count_by(self.goals_key)

    def save_unique(self):
        self._increment_by(self.unique_key)

    def save_goal(self):
        self._increment_by(self.goals_key)

    def clean_up_variant(self, unique, goals):
        if unique and int(self.get_unique()) >= unique:
            self._increment_by(self.unique_key, '-%d' % unique)
        if goals and int(self.get_goals()) >= goals:
            self._increment_by(self.goals_key, '-%d' % goals)

    def clean_up(self):
        self._del_by(self.unique_key)
        self._del_by(self.goals_key)
        self._del_by(self.details_key)


class TestData(object):
    def __init__(self, date=datetime.now().strftime('%Y-%m-%d'),
                 page_id=28025, variant_id=34924, profile_id=1, channel_id=1,
                 data_values=None, utm_params=None, additional_params=None):
        self.redis = RedisMetricsClient()
        self.data_values = data_values or [
            '91.195.136.52',
            time(),
            None,
        ]
        self.channel_id = channel_id
        self.utm_params = utm_params or {
            'utm_medium': 'cpc',
            'utm_campaign': 'распродажа',
            'utm_term': 'бег,обувь',
        }
        self.additional_params = additional_params or {
            'ad_label': 'Форма',
            'ad_type': 1,
            'ad_id': 10,
        }

        self.visitor = VisitorMetrics(variant_id, date, self.redis)
        self.hour = HourMetrics(variant_id, date, self.redis)
        self.total = TotalMetrics(page_id, self.redis)
        self.tariff = TariffStats(profile_id, date, self.redis)
        self.utm = UtmMetrics(variant_id, date, self.redis)

    def save(self):
        self.save_visitors()
        self.save_hours()
        self.save_total()
        self.save_tariff()
        self.save_utm()

    def flush(self):
        self.visitor.flush_db()
        self.hour.flush_db()
        self.total.flush_db()
        self.tariff.flush_db()
        self.utm .flush_db()

    def show(self):
        print '*'*25
        print 'Visits:'
        print '*'*25
        print 'unique:', self.visitor.get_unique()
        print 'visits:', self.visitor.get_visits()
        print 'goals:', self.visitor.get_goals()
        print 'additional:', self.visitor.get_additional_list()
        print 'details:', self.visitor.get_details()
        print 'geo:', self.visitor.get_geo()
        print 'variants:', self.visitor.get_variants()

        print ""

        print '*'*25
        print 'Hours:'
        print '*'*25
        print 'stats:', self.hour.get_hours_stats()

        print '*'*25
        print 'Total:'
        print '*'*25
        print 'unique:', self.total.get_unique()
        print 'goals:', self.total.get_goals()
        print 'conversions:', self.total.get_conversions()

        print '*'*25
        print 'Tariff:'
        print '*'*25
        print 'unique', self.tariff.get_unique()

        print '*'*25
        print 'Utm:'
        print '*'*25
        print 'utm', self.utm.get_utm()

    def save_visitors(self):
        self.visitor.save_visitor(is_unique=1, data=self.data_values)
        self.visitor.save_visitor(is_unique=0, data=self.data_values)
        self.visitor.save_goal(data=self.data_values)
        self.visitor.save_additional(ad_id=1, ad_type=1, ad_label='form')

    def save_hours(self):
        self.hour.save_visitor(is_unique=1)
        self.hour.save_lead()
        self.hour.save_goal()

    def save_total(self):
        self.total.save_unique()
        self.total.save_goal()

    def save_tariff(self):
        self.tariff.save_unique()

    def save_utm(self):
        self.utm.save_visit_with_utm(1, self.channel_id, self.utm_params)
        self.utm.save_utm_goal(
            self.channel_id, self.utm_params, self.additional_params)
