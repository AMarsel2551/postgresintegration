#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re

from setuptools import setup, find_packages


def get_version(package):
    """
    Return package version as listed in `__version__` in `init.py`.
    """
    with open(os.path.join(package, "__init__.py")) as f:
        return re.search("__version__ = ['\"]([^'\"]+)['\"]", f.read()).group(1)


setup(
    name="postgresintegration",
    version=get_version("ecomaiohttpclient"),
    packages=find_packages(),
    install_requires=[
        "ujson",
        "aiohttp",
        "pydantic"
    ],
)