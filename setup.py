#!/usr/bin/env python

from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = [r for r in f.read().splitlines() if 'git+' not in r]
    f.close()

setup(
    name='mjxproc',
    version='1.0',
    description="An Automated Workflow MJX Data Processing.",
    author="Ryan Hammonds",
    author_email='ryan.hammonds@utexas.edu',
    url='https://github.com/ryanhammonds/MJXProcessing',
    packages=['mjxproc'],
    entry_points={
        'console_scripts': [
            'mjxproc=mjxproc.mjxproc_run:main'
        ]
    },
    include_package_data=True,
    install_requires=requirements,
    license="GNU General Public License v3",
    zip_safe=False,
    keywords='',
    classifiers=[
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.6'
    ],
    test_suite='tests'
)
