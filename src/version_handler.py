#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging


def TagNumDict(version_file_path):
    tag_num_dict = {}
    with open(version_file_path, 'r') as file:
        for line in file.readlines():
            line = line.strip()
            tag = line.split('=')[0]
            num = line.split('=')[1]

            if not num.isdigit():
                raise ValueError("version number must be digit!")
            tag_num_dict[tag] = int(num)
    return tag_num_dict


def CurrentVersion(version_file_path):
    nums_list = list(TagNumDict(version_file_path).values())
    return _VersionStr(nums_list)


def _IncreaseVersion(nums_list, index):
    if not nums_list or index <= 0:
        raise Exception('nums list is empty or index < 0')

    index = index - 1
    if index >= len(nums_list):
        index = len(nums_list) - 1

    nums_list[index] += 1
    for i in range(index+1, len(nums_list)):
        nums_list[i] = 0


def _ToFile(version_dict, version_file_path):
    with open(version_file_path, 'w') as file:
        for key in version_dict:
            line = '%s=%s\n' % (key, version_dict[key])
            file.write(line)


def _VersionStr(num_list):
    version = ''
    for num in num_list:
        version += '%s.' % num

    if not version:
        raise ValueError("version string is empty")

    return version[:-1]


def Handle(version_index, version_file_path):
    tag_num_dict = TagNumDict(version_file_path)
    version_nums = list(tag_num_dict.values())
    if version_index <= 0:
        return _VersionStr(version_nums)

    logging.debug('before change: ' + str(version_nums))
    _IncreaseVersion(version_nums, version_index)
    logging.debug('after change: ' + str(version_nums))

    version_dict = dict(zip(tag_num_dict.keys(), version_nums))
    _ToFile(version_dict, version_file_path)

    return _VersionStr(version_nums)


if __name__ == "__main__":
    print(CurrentVersion('version.properties'))
