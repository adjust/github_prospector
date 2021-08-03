import os
from optparse import OptionParser

from QueryRunners import QueryRunner
from Reporter import ReporterTypes, Reporter
from utils import (validate_options, validate_and_get_repos, print_all_metrics, print_version,
                   parse_date,
                   print_rate_limits, validate_and_get_teams)

parser = OptionParser()
parser.add_option('-t', '--github_token', dest='github_token', default=os.environ.get('auditor_token'),
                  help="github's token for access to repos.\nCan set by env variable auditor_token")
parser.add_option('-o', '--owner', dest='owner', help='the username that repositories belong')
parser.add_option('-s', '--start_date', dest='start_date', help='filter metrics by start date')
parser.add_option('-e', '--end_date', dest='end_date', help='filter metrics by end date')
parser.add_option('-q', '--query', dest='query', help='query contains metric names split by comma')
parser.add_option('-l', '--metrics-list', dest='only_print_metrics', action='store_true', default=False,
                  help='list of all exising metrics')
parser.add_option('--out-dir', dest='output_dir', default=os.path.join(os.path.abspath('.'), 'runs'),
                  help=f"directory for storing reports. DEFAULT: {os.path.join(os.path.abspath('.'), 'runs')}")
parser.add_option('-f', '--format', choices=['json', 'csv', 'print'], dest='reporter_type', default='print',
                  help=f'Type of Reports: {ReporterTypes.get_all_reporters_types()}')
parser.add_option('--one-file', dest='one_file', action='store_true', default=False, help='create one-file report')
parser.add_option(
    '-V', '--version', dest='only_print_version', action='store_true', default=False, help='prints version')
parser.add_option('--get-limits', dest='only_print_limits', action='store_true', default=False,
                  help="prints github's rate limits")

parser.add_option('--repos', dest='repos', default=[], help='list of repos for analysis')
parser.add_option('--teams', dest='teams', default=[], help='list of teams for analysis')
parser.add_option('--users', dest='users', default=[], help='list of users for analysis')


def main(config):
    if getattr(config, 'only_print_metrics'):
        print_all_metrics()
        exit(0)

    if getattr(config, 'only_print_version'):
        print_version()
        exit(0)

    if getattr(config, 'only_print_limits'):
        print_rate_limits(config)
        exit(0)

    if not validate_options(config):
        print('Check arguments and options')
        exit(1)

    if getattr(config, 'start_date'):
        dt = getattr(config, 'start_date')
        setattr(config, 'start_date', parse_date(dt))

    if getattr(config, 'end_date'):
        dt = getattr(config, 'end_date')
        setattr(config, 'end_date', parse_date(dt))

    if getattr(config, 'repos'):
        repos = [i.strip() for i in getattr(config, 'repos').split(',')]
        validated_repos = validate_and_get_repos(repos, config)
        setattr(config, 'repos', validated_repos)

    if getattr(config, 'teams'):
        teams = [i.strip() for i in getattr(config, 'teams').split(',')]
        validated_teams = validate_and_get_teams(teams, config)
        setattr(config, 'teams', validated_teams)

    if getattr(config, 'users'):
        users = [i.strip() for i in getattr(config, 'users').split(',')]
        # here need to add validation for users
        setattr(config, 'users', users)

    if not getattr(config, 'query'):
        print('Set parameter query')
        exit(1)

    query = getattr(config, 'query')
    qr = QueryRunner(query, config)
    qr.run()
    for results in (qr.repos_results, qr.teams_results, qr.users_results):
        Reporter(results, config).run()


if __name__ == '__main__':
    (options, args) = parser.parse_args()
    main(options)
