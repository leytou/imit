#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os
import sys

sys.path.append(os.path.dirname(os.path.realpath(__file__)))  # noqa
import version_handler
import commit_inquirer
import config


def _GetCommitType(args, commit_types):
    for i in commit_types:
        if args[i]:
            return commit_types[i]
    return ""


def _GetVersionIndex(args):
    for i in range(1, 5):
        key = "-%d" % i
        if args[key]:
            return i
    return 0


def _GetCommitMsg(args):
    return args["-M"] if args["-M"] else args["<msg>"]


def UpdateOptionFromArgs(commit_option, args, commit_types):
    commit_type = _GetCommitType(args, commit_types)
    if commit_type and "commit_type" not in commit_option:
        commit_option["commit_type"] = commit_type

    version_index = _GetVersionIndex(args)
    if version_index > 0 and "version_index" not in commit_option:
        commit_option["version_index"] = version_index

    commit_title = _GetCommitMsg(args)
    if commit_title and "commit_title" not in commit_option:
        commit_option["commit_title"] = commit_title

    logging.debug("option from args: " + str(commit_option))


def UpdateOptionFromInquirer(commit_option, version_file_path, commit_types):
    version_processor = version_handler.VersionProcessor()
    version_dict = version_processor.TagNumDict()
    logging.debug("tag num dict: " + str(version_dict))

    if "commit_type" not in commit_option:
        answer = commit_inquirer.QType(list(commit_types.values()))
        commit_option.update(answer)
        logging.debug("option : " + str(answer))

    if "version_index" not in commit_option:
        answer = commit_inquirer.QVersion(
            version_dict.keys(), commit_option["commit_type"], version_file_path
        )
        commit_option.update(answer)
        logging.debug("option : " + str(answer))

    if "jira_id" not in commit_option:
        answer = commit_inquirer.QJiraId()
        commit_option.update(answer)
        logging.debug("option : " + str(answer))

    commit_style = config.Get("commit_style")
    commit_styles = ["title-only", "title-why-how-influence"]
    if commit_style not in commit_styles:
        commit_style = commit_inquirer.QCommitStyle(commit_styles)
        config.Write("commit_style", commit_style)
    logging.debug("commit_style:" + commit_style)

    if "commit_title" not in commit_option:
        answer = commit_inquirer.QMsg("title", False)
        commit_option.update(answer)
        logging.debug("option : " + str(answer))

    if commit_style == "title-only":
        return
    if commit_option["commit_type"] in ("docs", "test", "style"):
        return

    skippable = True
    if commit_option["commit_type"] in ("bugfix",):
        skippable = False

    if "commit_why" not in commit_option:
        answer = commit_inquirer.QMsg("why", skippable)
        commit_option.update(answer)
        logging.debug("option : " + str(answer))

    if "commit_how" not in commit_option:
        answer = commit_inquirer.QMsg("how", skippable)
        commit_option.update(answer)
        logging.debug("option : " + str(answer))

    if "commit_influence" not in commit_option:
        answer = commit_inquirer.QMsg("influence", skippable)
        commit_option.update(answer)
        logging.debug("option : " + str(answer))
