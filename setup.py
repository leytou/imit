#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name="imit",
    version="1.3.6",
    description="提供交互或命令行的形式规范地提交git commit",
    long_description="""提供交互或命令行的形式规范地提交git commit""",
    keywords="python commit git",
    author="leytou",
    author_email="hi_litao@163.com",
    url="https://github.com/leytou",
    license="MIT",
    include_package_data=True,
    zip_safe=False,
    python_requires=">=3.7",
    install_requires=["inquirer", "docopt", "GitPython", "jira", "pyDes"],
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
    entry_points={
        "console_scripts": [
            "imit = src.imit:main",
        ]
    },
)
