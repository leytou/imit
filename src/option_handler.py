#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os
import sys

sys.path.append(os.path.dirname(os.path.realpath(__file__)))  # noqa
import version_handler
import commit_inquirer


def _GetCommitType(args, commit_types):
    for i in commit_types:
        if args[i]:
            return commit_types[i]
    return ''


def _GetVersionIndex(args):
    for i in range(1, 5):
        key = '-%d' % i
        if args[key]:
            return i
    return 0


def _GetCommitMsg(args):
    return args['-M'] if args['-M'] else args['<msg>']


def UpdateOptionFromArgs(commit_option, args, commit_types):
    commit_type = _GetCommitType(args, commit_types)
    if commit_type and 'commit_type' not in commit_option:
        commit_option['commit_type'] = commit_type

    version_index = _GetVersionIndex(args)
    if version_index > 0 and 'version_index' not in commit_option:
        commit_option['version_index'] = version_index

    commit_msg = _GetCommitMsg(args)
    if commit_msg and 'commit_msg' not in commit_option:
        commit_option['commit_msg'] = commit_msg

    logging.debug('option from args: ' + str(commit_option))


def UpdateOptionFromInquirer(commit_option, version_file_path, commit_types):
    version_dict = version_handler.TagNumDict(version_file_path)
    logging.debug('tag num dict: ' + str(version_dict))

    # guess type by commit_msg:
    if 'commit_msg' in commit_option:
        for key_word in ['bug', '修复']:
            if key_word in commit_option['commit_msg']:
                guess_type = 'bugfix'
                pass

    if 'commit_type' not in commit_option:
        answer = commit_inquirer.QType(list(commit_types.values()), guess_type)
        commit_option.update(answer)
        logging.debug('option : '+str(answer))

    if 'version_index' not in commit_option:
        answer = commit_inquirer.QVersion(
            version_dict.keys(), commit_option['commit_type'], version_file_path)
        commit_option.update(answer)
        logging.debug('option : '+str(answer))

    if 'jira_id' not in commit_option:
        answer = commit_inquirer.QJiraId()
        commit_option.update(answer)
        logging.debug('option : '+str(answer))

    if 'commit_msg' not in commit_option:
        answer = commit_inquirer.QMsg()
        commit_option.update(answer)
        logging.debug('option : '+str(answer))
