#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import sys
import os
import inquirer
import shutil

if not sys.platform == 'win32':
    import readline

sys.path.append(os.path.dirname(os.path.realpath(__file__)))  # noqa
import version_handler


def _MsgValidation(answers, current, nullable):
    if nullable:
        return True
    if not current:
        raise inquirer.errors.ValidationError(
            '', reason='Please input commit message!')

    return True


def QType(types):
    question = inquirer.List('commit_type',
                             message='请选择commit类型',
                             choices=types,
                             carousel=True
                             )
    return inquirer.prompt([question])


def QVersion(tags, commit_type, version_file_path):
    tags_index_tagged = []
    version_processor = version_handler.VersionProcessor()
    nums = list(version_processor.TagNumDict().values())
    index = 0
    for tag in tags:
        tag += '\t(%s) ' % nums[index]
        index += 1
        tags_index_tagged.append((tag, index))
    # print(tags_index_tagged)
    current_version = version_processor.CurrentVersion()

    index = -1
    if commit_type == 'feature' or commit_type == 'refactor':
        index = -2

    question = inquirer.List('version_index',
                             message='请选择要增加的版本号(当前: %s)' % current_version,
                             choices=tags_index_tagged,
                             carousel=True,
                             default=tags_index_tagged[index][1]
                             )
    return inquirer.prompt([question])


def _GetActualSize(s):
    size = 0
    for i in s:
        if ord(i) <= 255:
            size += 1
        else:
            size += 2
    return size


def _LeftString(s, actual_size):
    output = ''
    size = 0
    for i in s:
        if ord(i) <= 255:
            size += 1
        else:
            size += 2

        if size > actual_size:
            return output
        else:
            output += i
    return output


def _JiraVisualHandle(issues):
    id_max_size = 0
    for i in issues:
        jira_id = i[0]
        size = _GetActualSize(jira_id)
        if size > id_max_size:
            id_max_size = size

    terminal_width = shutil.get_terminal_size((80, 20)).columns
    summary_max_width = terminal_width - \
        len('    ') - id_max_size - len(' ') - len('...')
    if summary_max_width < 5:
        summary_max_width = 5

    jira_ids = []
    for i in issues:  # i[0]is issues id, i[1] is issues summary
        jira_id = i[0]
        jira_summary = i[1]
        temp = jira_summary
        jira_summary = _LeftString(jira_summary, summary_max_width)
        if temp != jira_summary:
            jira_summary += '...'

        viusal_jira_id = jira_id.ljust(id_max_size)
        jira_ids.append((viusal_jira_id + ' ' + jira_summary, jira_id))
    return jira_ids


def QJiraId(from_server=False):
    jira_issues = __import__('jira_issues')
    print('正在加载jira 问题列表...')
    issues = []
    if from_server:
        issues = jira_issues.GetJiraIssuesFromServer()
    else:
        issues = jira_issues.GetJiraIssues()
    if not issues:
        print('加载jira 问题列表失败...')
        return {'jira_id': ''}

    all_jira_ids = _JiraVisualHandle(issues)
    filtered_ids = all_jira_ids.copy()

    while True:
        choices = [('无', '')] + filtered_ids + [
            ('↺【 刷新 】', '--refresh--'),
            ('🔍【 筛选 】', '--filter--')
        ]

        question = inquirer.List('jira_id',
                                message='请选择JIRA ID',
                                choices=choices,
                                carousel=True
                                )
        answer = inquirer.prompt([question])
        if not answer:  # 用户按Ctrl+C取消
            return {'jira_id': ''}
        
        if answer['jira_id'] == '--refresh--':
            return QJiraId(True)
        elif answer['jira_id'] == '--filter--':
            filter_text = input('请输入筛选关键字: ').strip().lower()
            if filter_text:
                # 根据关键字过滤JIRA ID和描述
                filtered_ids = [(display, id) for display, id in all_jira_ids 
                              if filter_text in display.lower() or filter_text in id.lower()]
                if not filtered_ids:
                    print('没有找到匹配的JIRA条目')
                    filtered_ids = all_jira_ids.copy()  # 如果没找到，恢复完整列表
            else:
                filtered_ids = all_jira_ids.copy()  # 如果输入空字符串，恢复完整列表
            continue
        else:
            return answer


def QMsg(field, skippable):
    while True:
        str = input('请输入commit %s：' % field + ('(按回车跳过)' if skippable else ''))
        if skippable and not str:
            return {'commit_%s' % field: ''}
        if str:
            return {'commit_%s' % field: str}

def QServerJiraToken():
    question = [
        inquirer.Text(
            'server', message='请输入JIRA主页面链接', validate=lambda _, x: x.startswith('http://') or x.startswith('https://')),
        inquirer.Password('api_token', message='请输入JIRA API token(JIRA右上角-用户信息-个人访问令牌)',
                          validate=lambda _, x: x != ''),
    ]
    return inquirer.prompt(question)

def QCommitStyle(styles):
    question = inquirer.List('commit_style',
                             message='请选择commit message风格(首次使用配置，后续通过配置文件(~/.imitrc.ini)修改)',
                             choices=styles,
                             carousel=True
                             )
    return inquirer.prompt([question])['commit_style']
