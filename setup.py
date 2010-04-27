#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name = "gsconfig.py",
    version = "1.0",
    description = "GeoServer REST Configuration Client",
    keywords = "GeoServer REST Configuration",
    license = "MIT",
    url = "http://bitbucket.org/dwins/gsconfigpy",
    author = "David Winslow, Sebastian Benthall",
    author_email = "dwinslow@opengeo.org",
    install_requires = ['httplib2'],
    package_dir = {'':'src'},
    packages = find_packages('src'),
    test_suite = "test.catalogtests"
) 

