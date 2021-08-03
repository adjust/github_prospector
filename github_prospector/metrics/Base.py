import importlib
import optparse
import os
import time
from datetime import datetime
from enum import Enum

from github import Github
from github.GithubException import RateLimitExceededException


DEFAULT_METRICS_DIR = os.path.dirname(os.path.realpath(__file__))

def github_rate_limit_decorator(func):
    """Decorator checking github limits and can make pause."""

    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except RateLimitExceededException:
            cls = args[0]  # get metric object for access to config
            g = Github(getattr(cls.config, 'github_token'))
            limits = g.get_rate_limit()
            remains_requests = limits.core.remaining
            max_requests = limits.core.limit
            reset_after = (limits.core.reset - datetime.utcnow()).total_seconds()
            print(f'Rate limit! {remains_requests}/{max_requests}. Auditor needs sleep for {reset_after} seconds')
            answ = input(f'Do you agree sleep for {reset_after} seconds? [y/N]').strip().upper()
            if answ == 'Y':
                reset_after = (limits.core.reset - datetime.utcnow()).total_seconds()
                if reset_after > 0:
                    time.sleep(reset_after + 1)
                return func(*args, **kwargs)

    return inner


def get_all_metrics():
    """Getting all metrics by getting all properties."""
    modules = [f'metrics.{i.split(".")[0]}' for i in os.listdir(DEFAULT_METRICS_DIR) if i.endswith('.py')]
    collected_metrics = {}
    for module in modules:
        if module == 'metrics.Base':
            continue
        tmp_module = importlib.import_module('github_prospector.' + module)
        for i in dir(tmp_module):
            if not i.endswith('Metrics'):
                continue
            cls: object = getattr(tmp_module, i)
            for name in __get_class_properties(cls):
                collected_metrics.update(
                    {f'{cls.__name__.lower()}.{name}': {
                        'class_name': f'{cls.__name__}',
                        'metric_name': f'{name}',
                        'module_name': f'{cls.__module__}',
                        'type': getattr(cls, 'MetricsType')

                    }}
                )
    return collected_metrics


def __get_class_properties(cls):
    """Return list of properties' names and endswith _metric."""
    return [k for k, v in vars(cls).items() if isinstance(v, property) and k.endswith('_metric')]


class MetricsTypes(Enum):
    BASE = 'BASE'
    USER = 'USER'
    TEAM = 'TEAM'
    REPO = 'REPO'


class BaseMetrics:
    MetricsType = MetricsTypes.BASE

    def __init__(self, config: optparse.Values, *args, **kwargs):
        self.config = config
        self.period_from = getattr(config, 'start_date', None)
        self.period_to = getattr(config, 'end_date', datetime.now())

    @property
    def all(self) -> dict:
        f"""Collect all properties in class and return as dict.
        Metrics:{self.__get_class_properties()}"""
        results = {}
        for prop in self.__get_class_properties():
            results[prop] = getattr(self, prop, None)
        return results

    def __get_class_properties(self):
        """Return list of properties' names and endswith _metric."""
        return [k for k, v in vars(self).items() if isinstance(v, property) and k.endswith('_metric')]
