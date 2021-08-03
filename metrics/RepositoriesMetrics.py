import optparse

from github.Commit import Commit
from github.Repository import Repository

from metrics.Base import github_rate_limit_decorator, BaseMetrics, MetricsTypes


class RepoMetrics(BaseMetrics):
    """Pulse metrics class."""

    MetricsType = MetricsTypes.REPO

    __prs_list = []
    __issues_list = []

    def __init__(self, config: optparse.Values, repository_data: Repository, *args, **kwargs):
        super().__init__(config, *args, **kwargs)
        self.repository_data = repository_data

    @github_rate_limit_decorator
    def __get_prs(self):
        if self.period_to and self.period_from:
            self.__prs_list = [pr for pr in self.repository_data.get_pulls('*')
                               if self.period_from <= pr.created_at <= self.period_to]

        elif self.period_from:
            self.__prs_list = [pr for pr in self.repository_data.get_pulls('*')
                               if self.period_from <= pr.created_at]

        elif self.period_to:
            self.__prs_list = [pr for pr in self.repository_data.get_pulls('*')
                               if self.period_to >= pr.created_at]
        else:
            self.__prs_list = [pr for pr in self.repository_data.get_pulls('*')]

    @github_rate_limit_decorator
    def get_merged_prs(self):
        if not self.__prs_list:
            self.__get_prs()
        return [pr for pr in self.__prs_list if pr.state == 'merged']

    @github_rate_limit_decorator
    def get_opened_prs(self):
        if not self.__prs_list:
            self.__get_prs()
        return [pr for pr in self.__prs_list if pr.state == 'open']

    @github_rate_limit_decorator
    def get_closed_prs(self):
        if not self.__prs_list:
            self.__get_prs()
        return [pr for pr in self.__prs_list if pr.state == 'closed']

    @property
    def closed_pr_metric(self):
        """Count of closed pull requests."""
        return len(self.get_closed_prs())

    @property
    def merged_prs_metric(self):
        """Count of merged pull requests."""
        return len(self.get_merged_prs())

    @property
    def opened_prs_metric(self):
        """Count of opened pull requests."""
        return len(self.get_opened_prs())

    @property
    def opened_issues_metric(self):
        """Count of opened issues."""
        return len(self.get_opened_issues())

    @property
    def closed_issues_metric(self):
        """Count of closed issues."""
        return len(self.get_closed_issues())

    @github_rate_limit_decorator
    def __get_issues(self):
        if self.period_to and self.period_from:
            self.__issues_list = [issue for issue in self.repository_data.get_issues()
                                  if self.period_from <= issue.created_at <= self.period_to]
        elif self.period_from:
            self.__issues_list = [issue for issue in self.repository_data.get_issues() if
                                  self.period_from <= issue.created_at]
        elif self.period_to:
            self.__issues_list = [issue for issue in self.repository_data.get_issues() if
                                  self.period_to >= issue.created_at]
        else:
            self.__issues_list = [issue for issue in self.repository_data.get_issues()]

    def get_opened_issues(self):
        if not self.__issues_list:
            self.__get_issues()
        return [issue for issue in self.__issues_list if issue.state == 'open']

    def get_closed_issues(self):
        if not self.__issues_list:
            self.__get_issues()
        return [issue for issue in self.__issues_list if issue.state == 'closed']

    def __repr__(self):
        return f'[{self.__class__.__name__}]<{self.repository_data.name}>'


class RepoCommitMetrics(BaseMetrics):
    MetricsType = MetricsTypes.REPO

    def __init__(self, config: optparse.Values, repository_data: Repository, *args, **kwargs):
        super().__init__(config, *args, **kwargs)
        self.repository = repository_data
        self._commits: list[Commit] = []

    @github_rate_limit_decorator
    def _get_commits(self) -> list[Commit]:
        if not self._commits:
            if self.period_from:
                self._commits = [i for i in self.repository.get_commits(since=self.period_from)]
            else:
                self._commits = [i for i in self.repository.get_commits()]
        return self._commits

    @property
    def commit_per_user_metric(self):
        """Collect commit info per repository."""
        results = {}

        for commit in self._get_commits():
            name = commit.author.name or commit.author.login
            _tmp = {
                'count': 1,
                'commits': [
                    {commit.sha: {
                        'last_modified': commit.last_modified
                    }}
                ]
            }
            prev_data = results.get(name)
            if prev_data is not None:
                _tmp['count'] = prev_data.get('count', 0) + _tmp.get('count', 0)
                _tmp['commits'] = prev_data.get('commits', []) + _tmp.get('commits', [])
            results[name] = _tmp
        results = {k: v for k, v in sorted(results.items(), key=lambda item: item[1].get('count'), reverse=True)}
        return results


class RepositoryInfoMetrics(BaseMetrics):
    """Info collected by repositories."""
    MetricsType = MetricsTypes.REPO

    def __init__(self, config: optparse.Values, repository: Repository, *args, **kwargs):
        super().__init__(config, *args, *kwargs)
        self.repository = repository

    @github_rate_limit_decorator
    def get_branch_info(self, branch):
        branch_data = {
            'name': branch.name,
            'protected': branch.protected,
        }
        if not branch.protected:
            return branch_data
        else:
            try:
                raw_protection_info = branch.get_protection().raw_data
            except AttributeError:
                branch_data['protection'] = "Can't access data"
                return branch_data

            restrictions = {
                'users': [user.get('login') for user in
                          raw_protection_info.get('restrictions', {}).get('users', {})],
                'teams': [team.get('name') for team in
                          raw_protection_info.get('restrictions', {}).get('teams', {})],
                'apps': [app.get('name') for app in raw_protection_info.get('restrictions', {}).get('apps', {})],
            }
            required_pull_request_reviews = {
                'dismiss_stale_reviews': raw_protection_info.get('required_pull_request_reviews', {}).get(
                    'dismiss_stale_reviews', {}),
                'require_code_owner_reviews': raw_protection_info.get('required_pull_request_reviews', {}).get(
                    'require_code_owner_reviews', {}),
                'required_approving_review_count': raw_protection_info.get('required_pull_request_reviews', {}).get(
                    'required_approving_review_count', {}),
            }

            enforce_admins = raw_protection_info.get('enforce_admins', {}).get('enabled')
            required_linear_history = raw_protection_info.get('required_linear_history', {}).get('enabled')
            allow_force_pushes = raw_protection_info.get('allow_force_pushes', {}).get('enabled')
            allow_deletions = raw_protection_info.get('allow_deletions', {}).get('enabled')

            branch_data['protection'] = {
                'restrictions': restrictions,
                'required_pull_request_reviews': required_pull_request_reviews,
                'enforce_admins': enforce_admins,
                'required_linear_history': required_linear_history,
                'allow_force_pushes': allow_force_pushes,
                'allow_deletions': allow_deletions,
            }
            return branch_data

    @property
    def get_branch_protection_metric(self):
        """Branch protection of repo."""
        result = {}
        for branch in self.repository.get_branches():
            result.update(
                {branch.name: self.get_branch_info(branch)}
            )
        return result

    @property
    def get_default_branch_metric(self):
        """Get Default branch."""
        return self.repository.default_branch
