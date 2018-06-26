#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'marshmallow',
    'requests',
    'urllib3',
    'bors',
    'click',
]

test_requirements = [
    'pytest',
    'tox',
    'coverage',
    'pytest-cov',
]


setup_requirements = ['pytest-runner', ]

setup(
    author="Bobby",
    author_email='karma0@gmail.com',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.6',
    ],
    description="A cryptocurrency trading bot",
    entry_points={
        'console_scripts': [
            'nombot=nombot.cli:main',
        ],
    },
    install_requires=requirements,
    license="GNU General Public License v3",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='nombot cryptocurrency bot',
    name='nombot',
    packages=find_packages(exclude=['tests', 'docs']),
    package_dir={'nombot': 'nombot'},
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/karma0/nombot',
    version='2.2.6',
    zip_safe=False,
)
