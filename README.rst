Site metrics
============


VisitorMetrics
--------------

.. code-block:: python

    from metrics.redis_wrapper import RedisMetricsClient
    from metrics  import VisitorMetrics
    from time import time


    date = '2014-06-18'
    redis = RedisMetricsClient()
    variant_id = 1
    data_values = [
        '91.195.136.52',
        time(),
        None,
    ]

    # Initialize metrics for defined date and page variant
    visitor = VisitorMetrics(variant_id, date, redis)
    # Get information about unique, visits and goals
    print visitor.get_unique(), visitor.get_visits(), visitor.get_goals()

    # Save unique visit
    visitor.save_visitor(is_unique=1, data=data_values)
    print visitor.get_unique(), visitor.get_visits(), visitor.get_goals()

    # Save not unique visit
    visitor.save_visitor(is_unique=0, data=data_values)
    print visitor.get_unique(), visitor.get_visits(), visitor.get_goals()

    # Save goal
    visitor.save_goal(data=data_values)
    print visitor.get_unique(), visitor.get_visits(), visitor.get_goals()

    # Save some additional params
    visitor.save_additional(ad_id=1, ad_type=1, ad_label='form')
    # Get all additional info for current variant
    print visitor.get_additional_list()

    # Get visits detailed information
    print [d for d in visitor.get_details()]

    # Get geo information
    print visitor.get_geo()

    # Get all used variants
    print visitor.get_variants()

    # Flush all visits data
    visitor.flush_db()


HourMetrics
-----------

.. code-block:: python

    from metrics.redis_wrapper import RedisMetricsClient
    from metrics  import HourMetrics

    date = '2014-06-18'
    redis = RedisMetricsClient()
    variant_id = 1

    # Initialize metrics for defined date and page
    hour = HourMetrics(variant_id, date, redis)
    # Get information about hours stats
    print hour.get_hours_stats()

    # Save unique visit
    hour.save_visitor(is_unique=1)
    print hour.get_hours_stats()

    # Save lead
    hour.save_lead()
    print hour.get_hours_stats()

    # Save goal
    hour.save_goal()
    print hour.get_hours_stats()

    # Flush all hours data
    hour.flush_db()


TotalMetrics
------------

.. code-block:: python

    from metrics.redis_wrapper import RedisMetricsClient
    from metrics  import TotalMetrics

    redis = RedisMetricsClient()
    page_id = 1

    # Initialize metrics for defined date and profile
    total = TotalMetrics(page_id, redis)

    # Save unique visit
    total.save_unique()
    print total.get_unique()

    # Save lead
    total.save_goal()
    print total.get_goals()

    # Get page conversion
    print total.get_conversions()

    # Flush all total visits data
    total.flush_db()


TariffStats
-----------

.. code-block:: python

    from metrics.redis_wrapper import RedisMetricsClient
    from metrics  import TariffStats

    redis = RedisMetricsClient()
    date = '2014-06-18'
    profile_id = 1

    # Initialize metrics for defined date and page variant
    tariff = TariffStats(profile_id, date, redis)

    # Save unique visit
    tariff.save_unique()
    print tariff.get_unique()

    # Flush all tariff data
    tariff.flush_db()


UtmMetrics
----------

.. code-block:: python

    from metrics.redis_wrapper import RedisMetricsClient
    from metrics  import UtmMetrics

    redis = RedisMetricsClient()
    date = '2014-06-18'
    variant_id = 1
    channel_id = 1

    utm_params = {
        'utm_medium': 'cpc',
        'utm_campaign': 'распродажа',
        'utm_term': 'бег,обувь',
    }
    additional_params = {
        'ad_label': 'Форма',
        'ad_type': 1,
        'ad_id': 10,
    }

    # Initialize metrics for defined date and page variant
    utm = UtmMetrics(variant_id, date, redis)
    print utm.get_utm()

    # Save utm unique visit
    utm.save_visit_with_utm(1, channel_id, utm_params)
    print utm.get_utm()

    # Save utm goal
    utm.save_utm_goal(channel_id, utm_params, additional_params)
    print utm.get_utm()

    # Flush all utm data
    utm.flush_db()

