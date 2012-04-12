#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

readme_text = file('README.rst', 'rb').read()

setup(name = "gsconfig",
    version = "0.5",
    description = readme_text,
    keywords = "GeoServer REST Configuration",
    license = "MIT",
    url = "http://github.com/opengeo/gsconfig.py",
    author = "David Winslow, Sebastian Benthall",
    author_email = "dwinslow@opengeo.org",
    maintainer = 'Ariel Núñez',
    maintainer_email = 'ingenieroariel@gmail.com',
    install_requires = ['httplib2'],
    package_dir = {'':'src'},
    packages = find_packages('src'),
    test_suite = "test.catalogtests",
    classifiers = [
                 'Development Status :: 4 - Beta',
                 'Intended Audience :: Developers',
                 'Intended Audience :: Science/Research',
                 'License :: OSI Approved :: MIT License',
                 'Operating System :: OS Independent',
                 'Programming Language :: Python',
                 'Topic :: Scientific/Engineering :: GIS',
                ]
) 

