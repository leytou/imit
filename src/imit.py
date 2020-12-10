#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Usage:
    imit.py config
    imit.py [-m|-b|-f|-R|-r] [-1|-2|-3|-4] [-M <msg>|<msg>] [-h|--help] [--log_level=<log_level>]

Options:
    -h,--help                   show usage
    -m                          set commit type: modify
    -b                          set commit type: bugfix
    -f                          set commit type: feature
    -R                          set commit type: refactor
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

sys.path.append(os.path.dirname(os.path.realpath(__file__)))  # noqa
import des
import config
import git_handler
import option_handler
import commit_inquirer
from pprint import pprint


def InitLogger(args):
    log_level = args["--log_level"]
    if log_level is None:

        log_level = "info"

    logging.basicConfig(level=logging._nameToLevel[log_level.upper()],
                        format='[%(levelname)s]: %(message)s')


def GetCommitOption(args, commit_types, version_file_path):
    commit_option = {}
    # 如果版本文件已修改过，则不再修改版本号(index设为0)
    if version_file_path in git_handler.AllChangedFiles():
        commit_option['version_index'] = 0

    option_handler.UpdateOptionFromArgs(commit_option, args, commit_types)
    option_handler.UpdateOptionFromInquirer(
        commit_option, version_file_path, commit_types)

    return commit_option


def EnvCheck(version_file_path):
    if sys.version_info < (3, 7):  # 3.7后dict默认为有序
        print('Please run imit with greater than python3.7.')
        exit(-1)

    git_root_path = git_handler.GetGitRootPath(os.getcwd())
    if not git_root_path:
        print('Please run imit in the git project path.')
        exit(-1)

    os.chdir(git_root_path)

    if not os.path.exists(version_file_path):
        print('File %s not found in current path.' % version_file_path)
        exit(-1)

    if not git_handler.StagedFiles():
        print('No staged file, exit commit.')
        exit(-1)


def Config():
    answer = commit_inquirer.QUsernamePassword()
    username = answer['username']
    password = answer['password']
    config.Write('username', des.DesEncrypt(username))
    config.Write('password', des.DesEncrypt(password))


def main():
    commit_types = {'-m': 'modify',
                    '-b': 'bugfix',
                    '-f': 'feature',
                    '-R': 'refactor',
                    '-r': 'revert', }
    version_file_path = 'version.properties'

    args = docopt.docopt(__doc__)
    InitLogger(args)
    logging.debug(args)

    if args['config']:
        Config()
        print('Username and password are encrypted and stored in file ~/.imitrc.ini')
        exit(0)

    EnvCheck(version_file_path)

    commit_option = GetCommitOption(args, commit_types, version_file_path)
    logging.debug('commit option: ' + str(commit_option))

    git_handler.Handle(commit_option, version_file_path)


if __name__ == "__main__":
    main()
