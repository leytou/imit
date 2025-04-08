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
api_token_config_key = 'api_token'


def GetJiraIssuesFromServer():
    server_en = config.Get(server_config_key)
    api_token_en = config.Get(api_token_config_key)
    if not server_en or not api_token_en:
        print("请通过'imit config' 配置JIRA网站路径和API token(在JIRA右上角-用户信息-个人访问令牌中创建)!")
        return []

    server = des.DesDecrypt(server_en)
    api_token = des.DesDecrypt(api_token_en)
    try:
        jira = JIRA(server=server,
                    token_auth=api_token,
                    timeout=5)
    except Exception as e:
        print("连接JIRA失败: %s，请检查JIRA网站路径/API token配置是否正确" % e)
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
