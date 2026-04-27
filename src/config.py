#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import configparser
import ast
import os

from pathlib import Path

from platformdirs import user_cache_dir

config_path = str(Path.home()) + "/.imitrc.ini"
cache_dir = user_cache_dir("imit")
cache_path = os.path.join(cache_dir, "cache.ini")
group = "user"


def _write_ini(path, key, value):
    config = configparser.RawConfigParser()
    parent = os.path.dirname(path)
    if parent and not os.path.exists(parent):
        os.makedirs(parent, exist_ok=True)
    if os.path.exists(path):
        config.read(path, encoding="utf-8")
    if group not in config.sections():
        config.add_section(group)
    config.set(group, key, value)
    with open(path, "w", encoding="utf-8") as configfile:
        config.write(configfile)


def _get_ini(path, key):
    config = configparser.RawConfigParser()
    if not os.path.exists(path):
        return ""
    config.read(path, encoding="utf-8")
    if config.has_option(group, key):
        return config.get(group, key)
    return ""


def _remove_ini(path, key):
    if not os.path.exists(path):
        return
    config = configparser.RawConfigParser()
    config.read(path, encoding="utf-8")
    if config.has_option(group, key):
        config.remove_option(group, key)
        with open(path, "w", encoding="utf-8") as configfile:
            config.write(configfile)


def Write(key, value):
    _write_ini(config_path, key, value)


def Get(key):
    return _get_ini(config_path, key)


def RemoveKey(key):
    _remove_ini(config_path, key)


def WriteCache(key, value):
    _write_ini(cache_path, key, value)


def GetCache(key):
    return _get_ini(cache_path, key)


def RemoveCache(key):
    _remove_ini(cache_path, key)
