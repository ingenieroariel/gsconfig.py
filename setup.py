#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name = "gsconfig",
    version = "0.5",
    description = "GeoServer REST Configuration Client",
    keywords = "GeoServer REST Configuration",
    license = "MIT",
    url = "http://github.com/opengeo/gsconfig.py",
    author = "David Winslow, Sebastian Benthall",
    author_email = "dwinslow@opengeo.org",
    install_requires = ['httplib2'],
    package_dir = {'':'src'},
    packages = find_packages('src'),
    test_suite = "test.catalogtests",
    classifiers   = [
                 'Development Status :: 4 - Beta',
                 'Intended Audience :: Developers',
                 'Intended Audience :: Science/Research',
                 'License :: OSI Approved :: MIT License',
                 'Operating System :: OS Independent',
                 'Programming Language :: Python',
                 'Topic :: Scientific/Engineering :: GIS',
) 

