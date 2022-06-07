#!/usr/bin/env python
from distutils.core import setup

setup(
    name="Hamlogger",
    version="1.0.0",
    author="Jakub Ondrusek",
    author_email="yak@gmx.co.uk",
    packages=["lib"],
    include_package_data=True,
    url="https://bitbucket.org/yak_sk/hamlogger",
    license="LICENSE",
    description="An amateur radio logging app",
    long_description=open("README.md").read(),
    install_requires=[
        "sqlalchemy",
    ],
)
