#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import os
import sys
import logging
from git.cmd import Git
from git import Repo
from pathlib import Path

sys.path.append(os.path.dirname(os.path.realpath(__file__)))  # noqa
import version_handler


def _GitCmd(cmd):
    git = Git(os.getcwd())
    _,stdout,stderr = git.execute(cmd, with_extended_output=True)
    print(stderr)
    return stdout


def _Add(path):
    cmd = ['git', 'add', path]
    _GitCmd(cmd)


def _Commit(msg):
    cmd = ['git', 'commit', '-m', msg]
    return _GitCmd(cmd)


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
    output = _GitCmd(cmd)
    logging.debug('changed files: ' + str(output))
    if not output:
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
