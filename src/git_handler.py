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


def _HasCommits():
    """Check if the repository has any commits."""
    try:
        git = Git(os.getcwd())
        git.rev_parse("HEAD")
        return True
    except:
        return False


def _ChangedFiles(cmd):
    try:
        success, output = _GitCmd(cmd)
        logging.debug('changed files: ' + str(output))
        if not success or not output:
            return []
        changed_files = output.split("\n")
        return changed_files
    except Exception as e:
        logging.debug(f'Error getting changed files: {str(e)}')


def GetGitRootPath(path):
    path = os.path.abspath(path)
    p = Path(path)
    git_file = p / '.git'
    if git_file.exists():
        return str(p)
    # If already at the root directory, return empty string
    if p.parent == p:
        return ''
    return GetGitRootPath(str(p.parent))


def AllChangedFiles():
    if not _HasCommits():
        # For first commit, get all staged files
        return StagedFiles()
    cmd = ['git', 'diff', '--name-only', 'HEAD']
    return _ChangedFiles(cmd)


def LastCommitVersion():
    if not _HasCommits():
        return None
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


def UnstagedFiles():
    """获取所有未暂存的文件，包括未追踪的新文件."""
    # 获取已修改但未暂存的文件
    modified_cmd = ['git', 'diff', '--name-only']
    modified_files = _ChangedFiles(modified_cmd) or []

    # 获取未追踪的文件
    untracked_cmd = ['git', 'ls-files', '--others', '--exclude-standard']
    untracked_files = _ChangedFiles(untracked_cmd) or []

    # 合并两个列表并去重
    all_unstaged = list(set(modified_files + untracked_files))
    return all_unstaged


def AddAll():
    """Add all changes to git staging area."""
    cmd = ['git', 'add', "*"]
    success, _ = _GitCmd(cmd)
    if not success:
        print("添加文件失败")
        exit(0)
    else:
        print("已添加所有文件到暂存区")


def Handle(commit_option, version_file_path):
    version_processor = version_handler.VersionProcessor()
    version_str_updated = version_processor.IncreaseVersionAndSave(
        commit_option['version_index'])

    msg_tags = [commit_option['commit_type'],
                version_str_updated, commit_option['jira_id']]
    commit_msg = _GenerateCommitMsg(msg_tags, commit_option['commit_title'], {"why": commit_option.get(
        'commit_why', None), "how": commit_option.get('commit_how', None), "influence": commit_option.get('commit_influence', None)})
    logging.debug('commit msg: ' + commit_msg)

    _Add(version_file_path)
    console_msg = _Commit(commit_msg)
    print(console_msg)


# if __name__ == "__main__":
    # _Add('test.py')
    # print(IsFileChanged('version.properties'))
    # _Commit('ABCDQWE')
