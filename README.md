GitHub Prospector
==========================
**Description:** CLI analytic tool for GitHub's teams, repositories, users.

**Contacts:** maksim.kuznetsov@akvelon.com, viktor.chaptsev@adjust.com or Development Efficiency Team

##Get metrics list
```shell
python3 __main__.py -l
```
##Install
```shell
pip install -r requirements.txt
```
##How to run
```shell
python3 __main__.py -q <metrics splitted by comma>
```
##Usage
```
Usage: __main__.py [options]

Options:
  -h, --help            show this help message and exit
  -t GITHUB_TOKEN, --github_token=GITHUB_TOKEN
                        github's token for access to repos. Can set by env
                        variable auditor_token
  -o OWNER, --owner=OWNER
                        the username that repositories belong
  -s START_DATE, --start_date=START_DATE
                        filter metrics by start date
  -e END_DATE, --end_date=END_DATE
                        filter metrics by end date
  -q QUERY, --query=QUERY
                        query contains metric names split by comma
  -l, --metrics-list    list of all exising metrics
  --out-dir=OUTPUT_DIR  directory for storing reports.
  -f REPORTER_TYPE, --format=REPORTER_TYPE
                        Type of Reports: ['json', 'print']
  --one-file            create one-file report
  -V, --version         prints version
  --get-limits          prints github's rate limits
  --repos=REPOS         list of repos for analysis
  --teams=TEAMS         list of teams for analysis
  --users=USERS         list of users for analysis
```
