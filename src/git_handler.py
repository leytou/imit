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
    cmd = ["git", "add", path]
    _GitCmd(cmd)


def _Commit(msg):
    cmd = ["git", "commit", "-m", msg]
    success, result = _GitCmd(cmd)

    # 如果提交成功，清除临时保存的提交信息
    if success:
        config.RemoveKey("temp_commit_title")
        config.RemoveKey("temp_commit_why")
        config.RemoveKey("temp_commit_how")
        config.RemoveKey("temp_commit_influence")

    return result


def _GenerateCommitMsg(msg_tags, msg_title, msg_fields):
    commit_msg = ""
    for i in msg_tags:
        if i:
            tag = "[%s]" % i
            commit_msg += tag

    commit_msg += " " + msg_title

    for key, value in msg_fields.items():
        if value:
            field = "%s: %s" % (key, value)
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
        logging.debug("changed files: " + str(output))
        if not success or not output:
            return []
        changed_files = output.split("\n")
        return changed_files
    except Exception as e:
        logging.debug(f"Error getting changed files: {str(e)}")


def GetGitRootPath(path):
    path = os.path.abspath(path)
    p = Path(path)
    git_file = p / ".git"
    if git_file.exists():
        return str(p)
    # If already at the root directory, return empty string
    if p.parent == p:
        return ""
    return GetGitRootPath(str(p.parent))


def AllChangedFiles():
    if not _HasCommits():
        # For first commit, get all staged files
        return StagedFiles()
    cmd = ["git", "diff", "--name-only", "HEAD"]
    return _ChangedFiles(cmd)


def LastCommitVersion():
    if not _HasCommits():
        return None
    cmd = ["git", "log", "-1", '--pretty=format:"%s"']
    success, output = _GitCmd(cmd)
    if not success:
        return None
    pattern = r"\[(\d+(\.\d+)+)\]"
    match = re.search(pattern, output)
    if not match:
        return None
    return str(match.group(1))


def StagedFiles():
    cmd = ["git", "diff", "--name-only", "--cached"]
    return _ChangedFiles(cmd)


def UnstagedFiles():
    """获取所有未暂存的文件，包括未追踪的新文件."""
    # 获取已修改但未暂存的文件
    modified_cmd = ["git", "diff", "--name-only"]
    modified_files = _ChangedFiles(modified_cmd) or []

    # 获取未追踪的文件
    untracked_cmd = ["git", "ls-files", "--others", "--exclude-standard"]
    untracked_files = _ChangedFiles(untracked_cmd) or []

    # 合并两个列表并去重
    all_unstaged = list(set(modified_files + untracked_files))
    return all_unstaged


def AddAll():
    """Add all changes to git staging area."""
    cmd = ["git", "add", "*"]
    success, _ = _GitCmd(cmd)
    if not success:
        print("添加文件失败")
        exit(0)
    else:
        print("已添加所有文件到暂存区")


def Handle(commit_option, version_file_path):
    version_processor = version_handler.VersionProcessor()
    version_str_updated = version_processor.IncreaseVersionAndSave(commit_option["version_index"])

    msg_tags = [commit_option["commit_type"], version_str_updated, commit_option["jira_id"]]
    commit_msg = _GenerateCommitMsg(
        msg_tags,
        commit_option["commit_title"],
        {
            "why": commit_option.get("commit_why", None),
            "how": commit_option.get("commit_how", None),
            "influence": commit_option.get("commit_influence", None),
        },
    )
    logging.debug("commit msg: " + commit_msg)

    _Add(version_file_path)
    console_msg = _Commit(commit_msg)
    print(console_msg)


# if __name__ == "__main__":
# _Add('test.py')
# print(IsFileChanged('version.properties'))
# _Commit('ABCDQWE')


def RunPreCommit():
    """如果项目存在.pre-commit-config.yaml，则执行pre-commit检查。

    Returns:
        True: 检查通过或不存在配置文件
        False: 检查失败
    """
    import shutil
    import subprocess
    import commit_inquirer

    pre_commit_config = os.path.join(os.getcwd(), ".pre-commit-config.yaml")
    if not os.path.exists(pre_commit_config):
        logging.debug("未找到.pre-commit-config.yaml，跳过pre-commit检查")
        return True

    # 检查pre-commit命令是否可用
    if not shutil.which("pre-commit"):
        print("警告: 检测到.pre-commit-config.yaml但系统未安装pre-commit")
        print("请通过 pip install pre-commit 安装")
        print("跳过pre-commit检查")
        return True

    # 检查pre-commit是否已安装到git hooks
    pre_commit_hook = os.path.join(os.getcwd(), ".git", "hooks", "pre-commit")
    if not os.path.exists(pre_commit_hook):
        print("检测到.pre-commit-config.yaml但pre-commit未安装到git hooks")
        answer = commit_inquirer.QConfirm("是否安装pre-commit到git hooks? (pre-commit install)")
        if answer["confirm"]:
            result = subprocess.run(["pre-commit", "install"], cwd=os.getcwd())
            if result.returncode != 0:
                print("pre-commit安装失败")
                return False
            print("pre-commit已安装到git hooks")
        else:
            print("跳过pre-commit检查")
            return True

    print("检测到.pre-commit-config.yaml，正在执行pre-commit检查...")
    staged_files = StagedFiles() or []
    result = subprocess.run(["pre-commit", "run", "--files"] + staged_files, cwd=os.getcwd())

    if result.returncode != 0:
        print("pre-commit检查未通过")
        return False

    print("pre-commit检查通过")
    return True
