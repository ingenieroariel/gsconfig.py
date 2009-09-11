#!/usr/bin/env python

from setuptools import setup

setup(name = "GSConfig",
    version = "1.0",
    description = "GeoServer REST Configuration Client",
    keywords = "GeoServer REST Configuration",
    license = "MIT",
    url = "http://bitbucket.org/dwins/gsconfigpy",
    author = "David Winslow, Sebastian Benthall",
    author_email = "dwinslow@opengeo.org",
    package_dir = {'':'lib'},
    test_suite = "test.suite.CatalogTests"
) 

