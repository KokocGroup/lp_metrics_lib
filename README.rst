LPG Metrics high-speed statistics storage
=========================================


VisitorMetrics
--------------

.. code-block:: python

    from metrics.redis_wrapper import RedisMetricsClient
    from metrics  import VisitorMetrics
    from datetime import datetime
    from time import time
    from pprintpp import pprint


    date = datetime.now().strftime('%Y-%m-%d')
    redis = RedisMetricsClient()
    variant_id = 34924
    data_values = [
        '91.195.136.52',
        time(),
        None,
    ]

    # Initialize metrics for defined date and page variant
    visitor = VisitorMetrics(variant_id, date, redis)
    # Get information about unique, visits and goals
    print(visitor.get_unique(), visitor.get_visits(), visitor.get_goals())

    # Save unique visit
    visitor.save_visitor(is_unique=1, data=data_values)
    print(visitor.get_unique(), visitor.get_visits(), visitor.get_goals())

    # Save not unique visit
    visitor.save_visitor(is_unique=0, data=data_values)
    print(visitor.get_unique(), visitor.get_visits(), visitor.get_goals())

    # Save goal
    visitor.save_goal(data=data_values)
    print(visitor.get_unique(), visitor.get_visits(), visitor.get_goals())

    # Save some additional params
    visitor.save_additional(ad_id=1, ad_type=1, ad_label='form')
    # Get all additional info for current variant
    pprint(visitor.get_additional_list())

    # Decrease goal
    visitor.decrease_goal(data=data_values)
    print(visitor.get_unique(), visitor.get_visits(), visitor.get_goals())

    # Decrease some additional params
    visitor.decrease_additional(ad_id=1, ad_type=1, ad_label='form')
    # Get all additional info for current variant
    pprint(visitor.get_additional_list())

    # Get visits detailed information
    pprint([d for d in visitor.get_details()])

    # Get geo information
    pprint(visitor.get_geo())

    # Get all used variants
    pprint(visitor.get_variants())

    # Flush all visits data
    visitor.flush_db()


HourMetrics
-----------

.. code-block:: python

    from metrics.redis_wrapper import RedisMetricsClient
    from metrics  import HourMetrics
    from datetime import datetime
    from pprintpp import pprint


    date = datetime.now().strftime('%Y-%m-%d')
    redis = RedisMetricsClient()
    variant_id = 34924

    # Initialize metrics for defined date and page
    hour = HourMetrics(variant_id, date, redis)
    # Get information about hours stats
    pprint(hour.get_hours_stats())

    # Save unique visit
    hour.save_visitor(is_unique=1)
    pprint(hour.get_hours_stats())

    # Save lead
    hour.save_lead()
    pprint(hour.get_hours_stats())

    # Save goal
    hour.save_goal()
    pprint(hour.get_hours_stats())

    # Decrease lead
    hour.decrease_lead()
    pprint(hour.get_hours_stats())

    # Decrease goal
    hour.decrease_goal()
    pprint(hour.get_hours_stats())

    # Flush all hours data
    hour.flush_db()


TotalMetrics
------------

.. code-block:: python

    from metrics.redis_wrapper import RedisMetricsClient
    from metrics  import TotalMetrics
    from pprintpp import pprint


    redis = RedisMetricsClient()
    page_id = 28025

    # Initialize metrics for defined date and profile
    total = TotalMetrics(page_id, redis)

    # Save unique visit
    total.save_unique()
    pprint(total.get_unique())

    # Save lead
    total.save_goal()
    pprint(total.get_goals())

    # Save lead
    total.decrease_goal()
    pprint(total.get_goals())

    # Get page conversion
    pprint(total.get_conversions())

    # Flush all total visits data
    total.flush_db()


TariffStats
-----------

.. code-block:: python

    from metrics.redis_wrapper import RedisMetricsClient
    from metrics  import TariffStats
    from datetime import datetime
    from pprintpp import pprint


    redis = RedisMetricsClient()
    date = datetime.now().strftime('%Y-%m-%d')
    profile_id = 1

    # Initialize metrics for defined date and page variant
    tariff = TariffStats(profile_id, date, redis)

    # Save unique visit
    tariff.save_unique()
    pprint(tariff.get_unique())

    # Flush all tariff data
    tariff.flush_db()


UtmMetrics
----------

.. code-block:: python

    from metrics.redis_wrapper import RedisMetricsClient
    from metrics  import UtmMetrics
    from datetime import datetime
    from pprintpp import pprint


    redis = RedisMetricsClient()
    date = datetime.now().strftime('%Y-%m-%d')
    variant_id = 34924
    channel_id = 1
    is_unique = 1

    utm_params = {
        'utm_medium': 'cpc',
        'utm_campaign': 'распродажа',
        'utm_term': 'бег,обувь',
    }
    additional_params = {
        'ad_label': 'Форма',
        'ad_type': 1, # 1 - form; 2 - link; 3 - payments; 4 - calls
        'ad_id': 10,
    }

    # Initialize metrics for defined date and page variant
    utm = UtmMetrics(variant_id, date, redis)
    pprint(utm.get_utm())

    # Save utm unique visit
    utm.save_visit_with_utm(is_unique, channel_id, utm_params)
    pprint(utm.get_utm())

    # Save utm goal
    utm.save_utm_goal(channel_id, utm_params, additional_params)
    pprint(utm.get_utm())

    # Save lead
    utm.decrease_utm_goal(channel_id, utm_params, additional_params)
    pprint(utm.get_utm())

    # Flush all utm data
    utm.flush_db()


Simple data for development
---------------------------

.. code-block:: python

    # save all
    from metrics.testing import TestData; TestData().save()

    # flush all
    from metrics.testing import TestData; TestData().flush()

    # show all
    from metrics.testing import TestData; TestData().show()
