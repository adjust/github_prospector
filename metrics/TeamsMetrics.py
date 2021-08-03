import optparse
from datetime import datetime

from github.NamedUser import NamedUser
from github.PullRequest import PullRequest
from github.Repository import Repository
from github.Team import Team

from metrics.Base import BaseMetrics, MetricsTypes, github_rate_limit_decorator


class TeamMetrics(BaseMetrics):
    MetricsType = MetricsTypes.TEAM

    def __init__(self, config: optparse.Values, team: Team, *args, **kwargs):
        super().__init__(config, *args, **kwargs)
        self.team = team
        self.members: list[NamedUser] = []
        self.repos: list[Repository] = []
        self.prs: dict[str, list[PullRequest]] = {}

    def _get_prs_only(self):
        if not self.prs:
            self._get_team_prs()
        res = []
        for pr_list in self.prs.values():
            res.extend(pr_list)
        return res

    @property
    def team_open_prs_count(self):
        """Open pull requests by team."""
        return len([pr for pr in self._get_prs_only() if pr.state == 'open'])

    @property
    def expired_open_prs_metric(self):
        """Expired Opened Pull Requests (more than 3 days)."""
        if not self.prs:
            self.prs = self._get_team_prs()
        results = {}
        for team_name, prs_data in self.prs.items():
            prs_data: list[PullRequest]
            _tmp = {}
            for pr in prs_data:
                exists_for = (datetime.now() - pr.created_at).days
                if exists_for >= 3:
                    _tmp['id'] = pr.id
                    _tmp['title'] = pr.title
                    _tmp['url'] = pr.html_url
                    _tmp['exists_for'] = f'{exists_for} days'
            if _tmp:
                results[team_name] = _tmp
        return results

    @property
    def open_pr_metric(self):
        """Open Pull Requests Info."""
        if not self.prs:
            self.prs = self._get_team_prs()
        results = {}
        for team_name, prs_data in self.prs.items():
            prs_data: list[PullRequest]
            _tmp = {}
            for pr in prs_data:
                _tmp['id'] = pr.id
                _tmp['title'] = pr.title
                _tmp['url'] = pr.html_url
                _tmp['author'] = f'{pr.user.name} | @{pr.user.login}'
                _tmp['reviewers'] = {
                    rev.user.name or rev.user.login: {'submitted_at': rev.submitted_at.isoformat(), 'state': rev.state}
                    for rev in pr.get_reviews()}
                _tmp['created_at'] = pr.created_at.isoformat()
                _tmp['updated_at'] = pr.updated_at.isoformat()
                _tmp['exists_for'] = f'{(datetime.now() - pr.created_at).days} days'
                # _tmp['comments'] = [
                #     {'body': c.body, 'author': c.user.name, 'created_at': c.created_at.isoformat()}
                #     for c in pr.get_comments()
                # ] too much data
            if _tmp:
                results[team_name] = _tmp
        return results

    @property
    def team_members_count_metric(self):
        """Get count team members."""
        return self._get_team_members().totalCount

    @property
    def team_open_prs_count_metric(self):
        """Get count of opened pull requests."""
        return len([i for i in self._get_prs_only() if i.state == 'open'])

    @github_rate_limit_decorator
    def _get_team_members(self):
        return self.team.get_members()

    @github_rate_limit_decorator
    def _get_team_repos(self) -> list[Repository]:
        if not self.repos:
            self.repos = self.team.get_repos()
        return self.repos

    @github_rate_limit_decorator
    def _get_team_prs(self):
        if not self.prs:
            _prs = {}
            for repo in self._get_team_repos():
                _tmp = repo.get_pulls()
                if self.period_to and self.period_from:
                    _tmp = [i for i in filter(
                        lambda x: self.period_to <= x.created_at <= self.period_from,
                        _tmp)]
                elif self.period_from:
                    _tmp = [i for i in filter(lambda x: x.created_at >= self.period_from, _tmp)]
                elif self.period_to:
                    _tmp = [i for i in filter(lambda x: x.created_at <= self.period_to, _tmp)]
                _prs[repo.name] = [i for i in _tmp]
            self.prs = _prs
        return self.prs
