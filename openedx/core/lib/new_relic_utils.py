"""
Contains utilities for working with New Relic.

These utilities will properly skip execution in an environment that does not use
New Relic.

"""

try:
    import newrelic.agent
except ImportError:
    newrelic = None  # pylint: disable=invalid-name


def add_new_relic_course_key_metrics(course_key):
    """
    Initialize metrics (course_id and org) for New Relic from a course_key, so
    we can slice data in New Relic Insights.

    """
    if not newrelic:
        return
    newrelic.agent.add_custom_parameter('course_id', unicode(course_key))
    newrelic.agent.add_custom_parameter('org', unicode(course_key.org))
