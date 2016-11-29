# -*- encoding: utf-8 -*-

__author__ = 'gotlium'

from time import time
from metrics import *


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
        print('*'*25)
        print('Visits:')
        print('*'*25)
        print('unique:', self.visitor.get_unique())
        print('visits:', self.visitor.get_visits())
        print('goals:', self.visitor.get_goals())
        print('additional:', self.visitor.get_additional_list())
        print('details:', self.visitor.get_details())
        print('geo:', self.visitor.get_geo())
        print('variants:', self.visitor.get_variants())

        print("")

        print('*'*25)
        print('Hours:')
        print('*'*25)
        print('stats:', self.hour.get_hours_stats())

        print('*'*25)
        print('Total:')
        print('*'*25)
        print('unique:', self.total.get_unique())
        print('goals:', self.total.get_goals())
        print('conversions:', self.total.get_conversions())

        print('*'*25)
        print('Tariff:')
        print('*'*25)
        print('unique', self.tariff.get_unique())

        print('*'*25)
        print('Utm:')
        print('*'*25)
        print('utm', self.utm.get_utm())

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
