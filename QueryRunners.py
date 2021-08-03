import importlib
import optparse

from github.NamedUser import NamedUser
from github.Repository import Repository
from github.Team import Team

from metrics.Base import get_all_metrics, MetricsTypes


class QueryRunner:
    """Class for working with query."""

    def __init__(self, queries: str, config: optparse.Values):

        self.config = config
        self.__queries = queries
        self.__existing_metrics = get_all_metrics()
        self.__existing_teams_metrics = {
            k: v for k, v in self.__existing_metrics.items() if v.get('type') == MetricsTypes.TEAM
        }
        self.__existing_repos_metrics = {
            k: v for k, v in self.__existing_metrics.items() if v.get('type') == MetricsTypes.REPO
        }
        self.__existing_users_metrics = {
            k: v for k, v in self.__existing_metrics.items() if v.get('type') == MetricsTypes.USER
        }
        self.parsed_queries = self.__validate_queries(self.__parse_queries(queries))
        self.repos: list[Repository] = getattr(config, 'repos')
        self.teams: list[Team] = getattr(config, 'teams')
        self.users: list[NamedUser] = getattr(config, 'users')
        self.repos_results: dict = {}
        self.teams_results: dict = {}
        self.users_results: dict = {}
        self.current_step = 0

    def __parse_queries(self, query: str):
        queries = [i.strip() for i in query.split(',')]
        if not ('all' in queries or 'ALL' in queries):
            return queries
        return self.__existing_metrics

    def __validate_queries(self, queries: list[str]):
        validated_queries = []
        for query in queries:
            if query in self.__existing_metrics:
                validated_queries.append(query)
            else:
                print(f'! {query} - not found and will be skip! Please check the name!')
        return validated_queries

    def print_status(self, prefix, name, metric_name):
        print(' ' * 100, end='\r')
        print(f'{prefix}: {name}, Metric: {metric_name} ✔', end='\r')

    def run(self):
        for metric_name in self.parsed_queries:
            if self.repos and metric_name in self.__existing_repos_metrics:
                self._run_repos_collect(metric_name)
            elif self.teams and metric_name in self.__existing_teams_metrics:
                self._run_teams_collect(metric_name)
            elif self.users and metric_name in self.__existing_users_metrics:
                self._run_users_collect()
            else:
                print(f'Metric: {metric_name} not found or you not set required parameters!')

    def _run_teams_collect(self, metric_name):
        self.current_step = 0
        for team in self.teams:
            team_name = team.name
            self.print_status('Team', team_name, metric_name)
            if self.teams_results.get(team_name) is None:
                self.teams_results[f'{team_name}'] = {metric_name: self.run_single(metric_name, team)}
            else:
                tmp = self.teams_results.get(team_name)
                results = self.run_single(metric_name, team)
                if not results:
                    continue
                tmp[metric_name] = self.run_single(metric_name, team)
                self.teams_results[team_name] = tmp
            self.current_step += 1
        self.__done('Teams')

    def _run_users_collect(self):
        pass

    def _run_repos_collect(self, metric_name):
        self.current_step = 0
        for repo in self.repos:
            repo_name = repo.name
            self.print_status('Repo', repo_name, metric_name)
            if self.repos_results.get(repo_name) is None:
                self.repos_results[repo_name] = {metric_name: self.run_single(metric_name, repo)}
            else:
                tmp = self.repos_results.get(repo_name)
                tmp[metric_name] = self.run_single(metric_name, repo)
                self.repos_results[repo_name] = tmp
            self.current_step += 1
        self.__done('Repos')

    def run_single(self, metric_name: str, obj: object):
        current_metric = self.__existing_metrics.get(metric_name)
        if not current_metric:
            print(f'Error, {current_metric} not found!')
            return {}
        module = importlib.import_module(current_metric['module_name'])
        _class = getattr(module, current_metric['class_name'])
        tmp = _class(self.config, obj)
        return getattr(tmp, current_metric['metric_name'])

    def __done(self, prefix: str = ''):
        print(' ' * 100, end='\r')
        print(f'{prefix} Done!\n{prefix} metrics collected: {self.current_step}')
