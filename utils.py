from github import UnknownObjectException, Github, BadCredentialsException
from github import Organization
import configparser


def get_repository_instances(repos: list[str]):
    repos_instances = []
    org = get_organization()
    for repo_name in repos:
        try:
            repos_instances.append(org.get_repo(repo_name))
        except UnknownObjectException:
            print(f'{repo_name} - Not found!')
    return repos_instances


def get_settings() -> configparser.ConfigParser:
    settings = configparser.ConfigParser()
    settings.read('settings.ini')
    return settings


def get_github(token: str):
    g = Github(token)
    try:
        g.get_rate_limit()
    except BadCredentialsException:
        print('Invalid github token!')
        exit(1)
    return g


def get_organization():
    settings = get_settings()
    org_name = settings.get('Github', 'organization')
    token = settings.get('Github', 'token')
    if not org_name:
        print('organization not found in settings.ini')
        exit(1)
    if not token:
        print('token not found in settings.ini')
        exit(1)
    g = get_github(token)
    try:
        org = g.get_organization(org_name)
    except UnknownObjectException:
        print('Organization not found!')
        exit(1)
    else:
        return org
