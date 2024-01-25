#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from jira import JIRA
import sys
import os
import ast

sys.path.append(os.path.dirname(os.path.realpath(__file__)))  # noqa
import config
import des

jira_filter = 'assignee = currentUser() AND resolution = Unresolved order by lastViewed DESC',

issues_config_key = 'issues'
server_config_key = 'server'
username_config_key = 'username'
password_config_key = 'password'


def GetJiraIssuesFromServer():
    server_en = config.Get(server_config_key)
    username_en = config.Get(username_config_key)
    password_en = config.Get(password_config_key)
    if not server_en or not username_en or not password_en:
        print("请通过'imit config' 配置JIRA网站路径，用户名和密码!")
        return []

    server = des.DesDecrypt(server_en)
    username = des.DesDecrypt(username_en)
    password = des.DesDecrypt(password_en)
    try:
        jira = JIRA(server=server,
                    basic_auth=(username, password),
                    timeout=5)
    except Exception as e:
        print("连接JIRA失败: %s，请检查JIRA网站路径/用户名/密码配置是否正确" % e)
        return []

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
