#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import os
import sys
import logging
import re
from git.cmd import Git
from git import Repo
from pathlib import Path


sys.path.append(os.path.dirname(os.path.realpath(__file__)))  # noqa
import version_handler
import config


def _GitCmd(cmd):
    git = Git(os.getcwd())
    status, stdout, stderr = git.execute(cmd, with_extended_output=True)
    print(stderr)
    return status == 0, stdout


def _Add(path):
    cmd = ['git', 'add', path]
    _GitCmd(cmd)

def _Commit(msg):
    cmd = ['git', 'commit', '-m', msg]
    success, result = _GitCmd(cmd)
    
    # 如果提交成功，清除临时保存的提交信息
    if success:
        config.RemoveKey('temp_commit_title')
        config.RemoveKey('temp_commit_why')
        config.RemoveKey('temp_commit_how')
        config.RemoveKey('temp_commit_influence')
    
    return result


def _GenerateCommitMsg(msg_tags, msg_title, msg_fields):
    commit_msg = ''
    for i in msg_tags:
        if i:
            tag = '[%s]' % i
            commit_msg += tag

    commit_msg += ' ' + msg_title

    for key, value in msg_fields.items():
        if value:
            field = '%s: %s' % (key, value)
            commit_msg += "\n" + field
    return commit_msg

def _ChangedFiles(cmd):
    success, output = _GitCmd(cmd)
    logging.debug('changed files: ' + str(output))
    if not success or not output:
        return []
    changed_files = output.split("\n")
    return changed_files


def GetGitRootPath(path):
    path = os.path.abspath(path)
    if path == '/':
        return ''

    git_file = Path(path+'/.git')
    if not (git_file.exists()):
        return GetGitRootPath(os.path.dirname(path))
    else:
        return path


def AllChangedFiles():
    cmd = ['git', 'diff', '--name-only', 'HEAD']
    return _ChangedFiles(cmd)

def LastCommitVersion():
    cmd = ['git', 'log', '-1', '--pretty=format:"%s"']
    success, output = _GitCmd(cmd)
    if not success:
        return None
    pattern = r'\[(\d+(\.\d+)+)\]'
    match = re.search(pattern, output)
    if not match:
        return None
    return str(match.group(1))


def StagedFiles():
    cmd = ['git', 'diff', '--name-only', '--cached']
    return _ChangedFiles(cmd)


def UnstaedFiles():
    cmd = ['git', 'diff', '--name-only']
    return _ChangedFiles(cmd)


def Handle(commit_option, version_file_path):
    version_processor = version_handler.VersionProcessor()
    version_str_updated = version_processor.IncreaseVersionAndSave(
        commit_option['version_index'])

    msg_tags = [commit_option['commit_type'],
                version_str_updated, commit_option['jira_id']]
    commit_msg = _GenerateCommitMsg(msg_tags, commit_option['commit_title'], {"why": commit_option.get('commit_why', None), "how": commit_option.get('commit_how', None), "influence": commit_option.get('commit_influence', None)})
    logging.debug('commit msg: ' + commit_msg)

    _Add(version_file_path)
    console_msg = _Commit(commit_msg)
    print(console_msg)


# if __name__ == "__main__":
    # _Add('test.py')
    # print(IsFileChanged('version.properties'))
    # _Commit('ABCDQWE')
