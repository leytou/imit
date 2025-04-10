#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Usage:
    imit.py config
    imit.py [-m|-f|-b|-c|-R|-t|-p|-d|-s|-r|-i|-u|-e] [-1|-2|-3|-4] [-M <msg>|<msg>] [-h|--help] [--log_level=<log_level>]

Options:
    -h,--help                   show usage
    -m                          set commit type: modify
    -f                          set commit type: feature
    -b                          set commit type: bugfix
    -c                          set commit type: chore
    -R                          set commit type: refactor
    -t                          set commit type: test
    -p                          set commit type: perf
    -d                          set commit type: doc
    -s                          set commit type: style
    -r                          set commit type: revert
    -1                          1st version number +1
    -2                          2nd version number +1
    -3                          3rd version number +1
    -4                          4th version number +1
    -M <msg>                    set commit message
    <msg>                       set commit message easily
    --log_level=<log_level>     set log level: notset,debug,info,warn,error,fatal,critical
"""


import logging
import docopt
import os
import sys

import git

sys.path.append(os.path.dirname(os.path.realpath(__file__)))  # noqa
import des
import config
import git_handler
import option_handler
import commit_inquirer
import version_handler
import fnmatch
from pprint import pprint


def InitLogger(args):
    log_level = args["--log_level"]
    if log_level is None:

        log_level = "info"

    logging.basicConfig(
        level=logging._nameToLevel[log_level.upper()],
        format="[%(levelname)s]: %(message)s",
    )


def GetCommitOption(args, commit_types, version_file_path, current_version):
    commit_option = {}
    if version_file_path.endswith("version.properties"):
        # 如果版本文件已修改过，则不再修改版本号(index设为0)
        if version_file_path in git_handler.AllChangedFiles():
            commit_option["version_index"] = 0
    else:
        last_version = git_handler.LastCommitVersion()
        # 如果当前版本号和上一次提交版本号不一致则认为已手动修改过
        if not last_version is None and last_version != current_version:
            commit_option["version_index"] = 0

    option_handler.UpdateOptionFromArgs(commit_option, args, commit_types)
    option_handler.UpdateOptionFromInquirer(
        commit_option, version_file_path, commit_types
    )

    return commit_option


def EnvCheck():
    if sys.version_info < (3, 7):  # 3.7后dict默认为有序
        print("Please run imit with greater than python3.7.")
        exit(-1)

    git_root_path = git_handler.GetGitRootPath(os.getcwd())
    if not git_root_path:
        print("Please run imit in the git project path.")
        exit(-1)

    os.chdir(git_root_path)

    if not git_handler.StagedFiles():
        # 显示未暂存的文件列表
        unstaged = git_handler.UnstagedFiles()
        if unstaged:
            print("未暂存的文件列表:")
            for file in unstaged:
                print("  " + file)
            print()
        else:
            print("没有已暂存或未暂存的文件")
            exit(0)

        answer = commit_inquirer.QConfirm("检测到没有已暂存的改动，是否执行 git add * ?")
        if answer["confirm"]:
            git_handler.AddAll()
        else:
            print("No staged file, exit commit.")
            exit(-1)


def Config():
    answer = commit_inquirer.QServerJiraToken()
    server = answer["server"]
    api_token = answer["api_token"]
    config.Write("server", des.DesEncrypt(server))
    config.Write("api_token", des.DesEncrypt(api_token))


def main():
    commit_types = {
        "-m": "modify",
        "-f": "feature",
        "-b": "bugfix",
        "-i": "improve",
        "-e": "depend",
        "-u": "build",
        "-R": "refactor",
        "-s": "style",
        "-t": "test",
        "-d": "doc",
        "-p": "perf",
        "-r": "revert",
        "-c": "chore",
    }

    args = docopt.docopt(__doc__)
    InitLogger(args)
    logging.debug(args)

    if args["config"]:
        Config()
        print("API token are encrypted and stored in file ~/.imitrc.ini")
        exit(0)

    EnvCheck()

    version_processor = version_handler.VersionProcessor()
    version_file_path = version_processor.file_path
    commit_option = GetCommitOption(
        args, commit_types, version_file_path, version_processor.CurrentVersion())
    logging.debug("commit option: " + str(commit_option))

    git_handler.Handle(commit_option, version_file_path)


if __name__ == "__main__":
    main()
