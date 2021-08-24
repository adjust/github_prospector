from datetime import datetime
from pprint import pprint

import click

from comments import get_comment_count, comments_count_and_depth
from utils import get_repository_instances


@click.group()
def main():
    pass


@main.command()
@click.option('--start-date', type=click.DateTime(formats=['%m-%d-%Y', '%m-%d-%Y %H:%M:%S']),
              default=datetime.now().date().strftime('%m-%d-%Y'))
@click.option('--end-date', type=click.DateTime(formats=['%m-%d-%Y', '%m-%d-%Y %H:%M:%S']),
              default=datetime.now().strftime('%m-%d-%Y %H:%M:%S'))
@click.option('--state', type=click.Choice(['all', 'open', 'closed', 'merged']), default='all')
@click.option('--repos', required=True)
def comments_count_by_repos(start_date, end_date, state, repos):
    print(f'Getting comments count by repositories')
    print(f'Period: {end_date - start_date}')
    print(f"PR's state: {state}")
    print(f'Repos: {repos}')
    repos_instances = get_repository_instances([i.strip() for i in repos.split(',')])
    results = get_comment_count(repos_instances, start_date, end_date, state)
    pprint(results)


@main.command()
@click.option('--start-date', type=click.DateTime(formats=['%m-%d-%Y', '%m-%d-%Y %H:%M:%S']),
              default=datetime.now().date().strftime('%m-%d-%Y'))
@click.option('--end-date', type=click.DateTime(formats=['%m-%d-%Y', '%m-%d-%Y %H:%M:%S']),
              default=datetime.now().strftime('%m-%d-%Y %H:%M:%S'))
@click.option('--state', type=click.Choice(['all', 'open', 'closed', 'merged']), default='all')
@click.option('--repos', required=True)
def comment_depth_by_repos(start_date, end_date, state, repos):
    print(f'Getting comments depth by repositories')
    print(f'Period: {end_date - start_date}')
    print(f"PR's state: {state}")
    print(f'Repos: {repos}')
    repos_instances = get_repository_instances([i.strip() for i in repos.split(',')])
    results = comments_count_and_depth(repos_instances, start_date, end_date, state)
    pprint(results)


if __name__ == '__main__':
    main()
