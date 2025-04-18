#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging

import os
import fnmatch

import re


def _VersionStr(num_list):
    version = ''
    for num in num_list:
        version += '%s.' % num

    if not version:
        raise ValueError("version string is empty")

    return version[:-1]


def _IncreaseVersion(nums_list, index):
    if not nums_list or index <= 0:
        raise Exception('nums list is empty or index < 0')

    index = index - 1
    if index >= len(nums_list):
        index = len(nums_list) - 1

    if isinstance(nums_list[index], int):
        nums_list[index] += 1
    elif isinstance(nums_list[index], str):
        digits = nums_list[index].split('.')
        digits[-1] = str(int(digits[-1]) + 1)
        nums_list[index] = '.'.join(digits)

    for i in range(index+1, len(nums_list)):
        nums_list[i] = 0


class PropertiesFile:
    def __init__(self, path):
        self.path = path

    def TagNumDict(self):
        tag_num_dict = {}
        with open(self.path, 'r') as file:
            for line in file.readlines():
                line = line.strip()
                tag = line.split('=')[0]
                num = line.split('=')[1]

                if not num.isdigit():
                    raise ValueError("version number must be digit!")
                tag_num_dict[tag] = int(num)
        return tag_num_dict

    def WriteToFile(self, version_dict):
        with open(self.path, 'w', newline='\n') as file:
            for key in version_dict:
                line = '%s=%s\n' % (key, version_dict[key])
                file.write(line)


class PodspecFile:
    def __init__(self, path):
        self.path = path

    def _ParameterName(self, file_content):
        match = re.search(r'Pod::Spec.new\s*do\s*\|(.*?)\|', file_content)
        if match:
            return match.group(1)
        return ''

    def _VersionRegPattern(self, file_content):
        return self._ParameterName(file_content) + r"\.version\s*=\s*'(\d+(\.\d+)*)'"
        # return '('+self._ParameterName(file_content) + r"\.version\s*=\s*'(\d+(\.\d+)*)')"

    def TagNumDict(self):
        tag_num_dict = {}
        with open(self.path, mode='r', encoding='utf-8') as file:
            file_content = file.read()
            pattern = self._VersionRegPattern(file_content)
            match = re.search(pattern, file_content)
            if match:
                version_str = match.group(1)
                versions = version_str.split('.')
                v_list = ['x', 'y', 'z', 'm', 'n']
                for i in range(len(versions)):
                    tag_num_dict[v_list[i]] = int(versions[i])
                return tag_num_dict
        return tag_num_dict

    def WriteToFile(self, version_dict):
        # 写得丑陋且低效
        with open(self.path, mode='r+', encoding='utf-8') as file:
            file_content = file.read()
            pattern = self._VersionRegPattern(file_content)
            file.seek(0)
            file_content_lines = file.readlines()
            for line in file_content_lines:
                match = re.search(pattern, line)
                if match:
                    version_nums = list(version_dict.values())
                    updated_version_str = _VersionStr(version_nums)
                    updated_line = line.replace(
                        match.group(1), updated_version_str)
                    file_content = file_content.replace(line, updated_line)

                    file.seek(0)
                    file.write(file_content)
                    file.truncate()

class XcodeProjectFile:
    def __init__(self, xcodeproj_path):
        self.xcodeproj_path = xcodeproj_path
        self.path = os.path.join(xcodeproj_path, 'project.pbxproj')

    def TagNumDict(self):
        tag_num_dict = {}
        with open(self.path, 'r', encoding='utf-8') as file:
            content = file.read()
            pattern = r'MARKETING_VERSION\s*=\s*(\d+(\.\d+)*);'
            match = re.search(pattern, content)
            if match:
                version_str = match.group(1)
                versions = version_str.split('.')
                v_list = ['x', 'y', 'z', 'm', 'n']  # 限制为4位版本号
                for i, v in enumerate(versions):
                    if i < len(v_list):
                        tag_num_dict[v_list[i]] = int(v)
        return tag_num_dict

    def WriteToFile(self, version_dict):
        current_version = self.TagNumDict()
        # 更新当前版本号，只修改已更改的部分
        for key in version_dict:
            if key in current_version:
                current_version[key] = version_dict[key]
        
        new_version = '.'.join(str(current_version.get(key)) for key in ['x', 'y', 'z', 'm', 'n'] if key in current_version)
        with open(self.path, 'r', encoding='utf-8') as file:
            content = file.read()

        pattern = r'(MARKETING_VERSION\s*=\s*)\d+(\.\d+)*;'
        new_content = re.sub(pattern, lambda m: f"{m.group(1)}{new_version};", content)

        with open(self.path, 'w', encoding='utf-8') as file:
            file.write(new_content)

class ConanFile:
    def __init__(self, conanfile_path):
        self.path = conanfile_path

    def TagNumDict(self):
        tag_num_dict = {}
        with open(self.path, 'r', encoding='utf-8') as file:
            content = file.read()
            pattern = r'version\s?=\s?"(\d+(\.\d+)+)"'
            match = re.search(pattern, content)
            if match:
                version_str = match.group(1)
                versions = version_str.split('.')
                first_major = versions.pop(0) if len(versions) == 4 else None
                v_list = ['major', 'minor', 'patch']
                for i, v in enumerate(versions):
                    if i < len(v_list):
                        tag_num_dict[v_list[i]] = int(v)
                if not first_major is None:
                    tag_num_dict["major"] = f"{first_major}.{tag_num_dict['major']}"
        return tag_num_dict

    def WriteToFile(self, version_dict):
        current_version = self.TagNumDict()
        for key in version_dict:
            if key in current_version:
                current_version[key] = version_dict[key]
        
        new_version = '.'.join(str(current_version.get(key)) for key in ['major', 'minor', 'patch'] if key in current_version)
        with open(self.path, 'r', encoding='utf-8', newline='') as file:
            content = file.read()

        pattern = r'(version\s?=\s?)"\d+(\.\d+)+"'
        new_content = re.sub(pattern, lambda m: f"{m.group(1)}\"{new_version}\"", content)

        with open(self.path, 'w', encoding='utf-8', newline='') as file:
            file.write(new_content)


class VersionProcessor:
    def __init__(self, start_path='.'):
        self.start_path = os.path.abspath(start_path)
        files = ['version.properties', '*.podspec', '*.xcodeproj', "conanfile.py"]
        self.file_path = self._FindVersionFile(self.start_path, files)
        if self.file_path == '':
            print('Version file %s not found in path %s or its subdirectories.' % (files, self.start_path))
            exit(1)
        logging.debug('version file path: ' + self.file_path)

        if self.file_path.endswith('.properties'):
            self.version_file = PropertiesFile(self.file_path)
        elif self.file_path.endswith('.podspec'):
            self.version_file = PodspecFile(self.file_path)
        elif self.file_path.endswith('.xcodeproj'):
            self.version_file = XcodeProjectFile(self.file_path)
        elif self.file_path.endswith('conanfile.py'):
            self.version_file = ConanFile(self.file_path)
        else:
            print('Unsupported version file format.')
            exit(1)

    def _FindVersionFile(self, directory, match_list):
        for match_pattern in match_list:
            file_list = os.listdir(directory)
            file_list.sort(key=len)  # 文件名短的在前面，避免拷贝的副本在前面
            for file in file_list:
                if fnmatch.fnmatch(file, match_pattern):
                    return file
        return ''

    def CurrentVersion(self):
        nums_list = list(self.version_file.TagNumDict().values())
        return _VersionStr(nums_list)

    def TagNumDict(self):
        return self.version_file.TagNumDict()

    def IncreaseVersionAndSave(self, version_index):
        tag_num_dict = self.version_file.TagNumDict()
        nums_list = list(tag_num_dict.values())
        if version_index <= 0:
            return _VersionStr(nums_list)

        _IncreaseVersion(nums_list, version_index)
        version_dict = dict(zip(tag_num_dict.keys(), nums_list))
        self.version_file.WriteToFile(version_dict)

        return _VersionStr(nums_list)


if __name__ == "__main__":
    handler = VersionProcessor()
    print(handler.CurrentVersion())
    print(handler.IncreaseVersionAndSave(3))
