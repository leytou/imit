#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import configparser
import ast
import os

from pathlib import Path

config_path = str(Path.home()) + '/.imitrc.ini'
group = 'user'


def Write(key, value):
    config = configparser.ConfigParser()
    if os.path.exists(config_path):
        config.read(config_path, encoding="utf-8")
    if group not in config.sections():
        config.add_section(group)

    config.set(group, key, value)
    with open(config_path, 'w') as configfile:
        config.write(configfile)


def Get(key):
    config = configparser.ConfigParser()
    if not os.path.exists(config_path):
        return ''

    config.read(config_path, encoding="utf-8")
    if config.has_option(group, key):
        return config.get(group, key)
    return ''
