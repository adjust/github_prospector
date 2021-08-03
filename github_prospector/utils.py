import importlib
import optparse
import os
from datetime import datetime
from typing import Iterable

from github import Github  # install PyGithub
from github.GithubException import UnknownObjectException

from github_prospector.__version__ import __version__
from github_prospector.metrics.Base import __get_class_properties

DATE_PATTERN = "%m-%d-%Y"


def print_version():
    print(f'Current auditor version: {__version__}')


def print_rate_limits(config):
    g = Github(config.github_token)
    limits = g.get_rate_limit()
    remains_requests = limits.core.remaining
    max_requests = limits.core.limit
    reset_after = (limits.core.reset - datetime.utcnow()).total_seconds()
    print(f'Rate limits:{remains_requests}/{max_requests}. For renew: {reset_after} seconds')


def validate_options(opt: optparse.Values):
    return all([
        getattr(opt, 'github_token'),
        validate_date(getattr(opt, 'start_date')),
        validate_date(getattr(opt, 'end_date')),
    ])


def validate_date(s):
    if isinstance(s, datetime):
        return True
    if s is None:
        return True
    try:
        datetime.strptime(s, DATE_PATTERN)
    except ValueError:
        print("Not a valid date: '{0}'. Valid date pattern {1}".format(s, DATE_PATTERN))
        return False
    return True


def parse_date(s):
    if isinstance(s, datetime):
        return s
    return datetime.strptime(s, DATE_PATTERN)


def print_all_metrics():
    print("All existing metrics: ")
    modules = [
        f'metrics.{i.split(".")[0]}' for i in os.listdir(os.path.join(
            os.path.abspath('.'), 'github_prospector', 'metrics'
        )) if i.endswith('.py')
    ]
    for module in modules:
        if module == 'metrics.Base':
            continue
        tmp_module = importlib.import_module('github_prospector.' + module)
        for i in dir(tmp_module):
            if not i.endswith('Metrics'):
                continue
            cls: object = getattr(tmp_module, i)
            for name in __get_class_properties(cls):
                if cls:
                    print(f'{cls.__name__.lower()}.{name}', f'Desc: {getattr(cls, name).__doc__}')


def validate_and_get_repos(repos: list[str], config: optparse.Values):
    validated_repos = []
    owner = getattr(config, 'owner')
    if 'all' in repos or 'ALL' in repos:
        if owner:
            return [
                i for i in Github(getattr(config, 'github_token')).get_organization(owner).get_repos()
            ]
        else:
            print('You need set owner before using all')
            exit(1)

    instances = []

    for repo_name in repos:
        if repo_name.find('/') == -1:
            if owner:
                validated_repos.append(f'{owner}/{repo_name}')
            else:
                print(f'{repo_name} not found! Set owner in cli or add name like OWNER/REPO_NAME')
                continue
        else:
            validated_repos.append(repo_name)

    g = Github(getattr(config, 'github_token'))
    for repo in validated_repos:
        instances.append(g.get_repo(repo))
    return instances


def filter_between(_iter: Iterable[object], value: str, less_than=None, more_than=None) -> filter:
    if less_than and more_than:
        return filter(lambda x: more_than <= getattr(x, value) <= less_than, _iter)
    elif less_than:
        return filter(lambda x: getattr(x, value) <= less_than, _iter)
    elif more_than:
        return filter(lambda x: getattr(x, value) >= more_than, _iter)
    else:
        return filter(lambda x: x, _iter)


def validate_and_get_teams(teams: list[str], config: optparse.Values):
    owner = getattr(config, 'owner')
    if not owner:
        print('Please set -o argument with owner')
        exit(1)

    g = Github(getattr(config, 'github_token'))
    org = g.get_organization(owner)

    if 'all' in teams or 'ALL' in teams:
        return [
            i for i in org.get_teams()
        ]
    instances = []
    for team_name in teams:
        try:
            instances.append(org.get_team_by_slug(team_name))
        except UnknownObjectException:
            print(f'{team_name} not found!')
    return instances
