#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from jira import JIRA
import sys
import os
import ast

sys.path.append(os.path.dirname(os.path.realpath(__file__)))  # noqa
import config
import des

jira_issues_api = 'https://jira.cvte.com/issues/?jql='

jira_filter = 'assignee = currentUser() AND resolution = Unresolved order by lastViewed DESC',

issues_config_key = 'issues'
username_config_key = 'username'
password_config_key = 'password'


def GetJiraIssuesFromServer():
    username_en = config.Get(username_config_key)
    password_en = config.Get(password_config_key)
    if not username_en or not password_en:
        print("请通过'imit config' 配置Jenkines用户名和密码!")
        return []

    username = des.DesDecrypt(username_en)
    password = des.DesDecrypt(password_en)
    jira = JIRA(server='https://jira.cvte.com/',
                basic_auth=(username, password),
                timeout=5)

    issues_list = [(issues.key, issues.fields.summary)
                   for issues in jira.search_issues(jira_filter)]
    config.Write(issues_config_key, str(issues_list).strip('[]'))
    return issues_list


def GetJiraIssuesFromConfig():
    issues_str = config.Get(issues_config_key)
    if not issues_str:
        return []

    issues_list = list(ast.literal_eval(issues_str))
    return issues_list


def GetJiraIssues():
    issues_list = GetJiraIssuesFromConfig()
    if not issues_list:
        issues_list = GetJiraIssuesFromServer()

    return issues_list
