# coding: utf-8

import sys
import requests
import datetime
from collections import Counter
import argparse
import traceback
import getpass


def get_stat_repo(url, date_begin='1970-01-01T00:00:00Z', date_end='3000-12-31T23:59:59Z', branch='master'):
    '''
    The function returns repository statistics (Github login/password required):
        1. The most active participants for a given period
        2. The number of open and closed pull requests for a given period of time, for a given branch
        3. The number of “old” pull requests for a given period of time, for a given branch (pull request is considered
            old, if it does not close within 30 days and is still open)
        4. The number of open and closed issues for a given period of time by the date the issue was created
        5. The number of “old” issues for a given period of time according to the date the issue was created
    (issue is considered old if it does not close within 14 days).
    Errors during repository processing are recorded in 'error.log'
    :param url: The URL github-repository
    :param date_begin: Date from which to take statistics
    :param date_end: Date by which to take statistics
    :param branch: Branch of repository for analysis (by default: 'master')
    :return: Displays tables in the following order:
        1. The most active users
        2. The number of open and closed pull requests for a given period of time
        3. The number of “old” pull requests for a given period of time by the creation date
        4. The number of open and closed issues for a given period of time by date
        5. The number of “old” issues for a given period of time by the date the issue was created.

    Example:
        python get_stat_repo.py --url=https://github.com/WillKoehrsen/Data-Analysis --date_begin=2020-05-25T00:00:00Z --date_end=2020-06-29T23:59:59Z --branch=master
    '''

    url_repo = url.split(sep='/')[-2:]
    date_begin = convert_string_to_iso_date(date_begin)
    date_end = convert_string_to_iso_date(date_end)
    try:
        url_repo_api = 'https://api.github.com/repos/' + url_repo[0] + '/' + url_repo[1]
    except IndexError:
        print(f'Incorrect URL of repo {url}. See error.log')
        write_log(f'Incorrect URL of repo {url}.\n')
        sys.exit(1)

    username = input('Github login: ')
    password = getpass.getpass('Github pass: ')

    data_commits = get_data(url_repo_api + '/commits', branch, username=username, password=password)
    print(get_top_authors(data_commits, date_begin, date_end, 30))
    data_pulls = get_data(url_repo_api + '/pulls', branch, username=username, password=password)
    count_pulls = get_count(data_pulls, date_begin, date_end)
    for k, v in count_pulls.items():
        print(f'Count pulls in state "{k}": {v}')
    print(f'Count of old pulls: {get_count_old(data_pulls, 30)}')
    data_issues = get_data(url_repo_api + '/issues', branch, username=username, password=password)
    count_issues = get_count(data_issues, date_begin, date_end)
    for k, v in count_issues.items():
        print(f'Count issues in state "{k}": {v}')
    print(f'Count of old issues: {get_count_old(data_issues, 14)}')


def get_data(url, branch, username, password):
    obj = url.split('/')[-1:]
    req_params = ''
    if obj[0] == 'commits':
        req_params = {'state': 'all', 'sha': branch}
    if obj[0] == 'pulls':
        req_params = {'state': 'all', 'base': branch}
    if obj[0] == 'issues':
        req_params = {'state': 'all'}

    res = requests.get(url, params=req_params, auth=(username, password))
    if res.ok:
        data = res.json()
        while 'next' in res.links.keys():
            res = requests.get(res.links['next']['url'], params=req_params, auth=(username, password))
            data.extend(res.json())
        return data
    else:
        print('Getting data by URL failed. See error.log')
        write_log(f'{res.url}: {str(res.status_code)}\n')
        sys.exit(1)


def get_top_authors(data, begin, end, top_count=30):
    commits = [row for row in data
               if begin <= convert_string_to_iso_date(row['commit']['author']['date']) <= end]
    if 'message' not in commits:
        dct_authors = {}
        for commit in commits:
            try:
                if commit['author']['login'] not in dct_authors:
                    dct_authors[commit['author']['login']] = 1
                else:
                    dct_authors[commit['author']['login']] += 1
            except Exception as e:
                write_log(f'{str(datetime.datetime.now())}: {str(e)}')
        result = Counter(dct_authors)
        top_authors = result.most_common(top_count)
        print('{:^20}|{:>5}'.format('Login', 'Commits'))
        print('_' * 30)
        for author in top_authors:
            print('{:^20}|{:>5}'.format(author[0], author[1]))
    elif commits['message'] == 'Not Found':
        print('Authors not found')
        return
    else:
        write_log(commits['message'])
        return


def get_count(raw_data, begin, end):
    data = [row for row in raw_data
            if begin <= convert_string_to_iso_date(row['created_at']) <= end]
    count_dct = {'open': 0, 'closed': 0}
    for row in data:
        try:
            if row['state'] == 'open':
                count_dct['open'] += 1
            elif row['state'] == 'closed':
                count_dct['closed'] += 1
        except Exception as e:
            with open('error.log', 'w') as log:
                log.write(str(e))
    return count_dct


def get_count_old(data, days_to_old=14):
    now = datetime.datetime.now()
    count_old = 0
    try:
        for row in data:
            if (convert_string_to_iso_date(row['created_at']) <= now - datetime.timedelta(days=days_to_old)) and (
                    row['state'] == 'open'):
                count_old += 1
    except Exception:
        write_log(traceback.format_exc())
        return
    return count_old


def convert_string_to_iso_date(date_string):
    return datetime.datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%SZ")


def write_log(event):
    with open('error.log', 'a') as log:
        log.write(f'{str(datetime.datetime.now())}: \t {str(event)}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='test task')
    parser.add_argument("--url", required=True, type=str, help="URL of Github repo")
    parser.add_argument("--date_begin", default='1970-01-01T00:00:00Z', help="Date begin")
    parser.add_argument("--date_end", default='3000-12-31T23:59:59Z', help="Date end")
    parser.add_argument("--branch", default='master', help="Branch")
    args = parser.parse_args()
    url = args.url
    date_begin = args.date_begin
    date_end = args.date_end
    branch = args.branch

    try:
        get_stat_repo(url=url, date_begin=date_begin,
                      date_end=date_end, branch=branch)
    except Exception as e:
        write_log(traceback.format_exc())
        print('An error has occurred. Details in the log file error.log')
        sys.exit(1)
