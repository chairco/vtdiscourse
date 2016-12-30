# -*- coding: utf-8 -*-
"""
    vtdiscourse
    ~~~~

    This is g0v vTaiwan Project, it's can help develope easy create topic on talk vTaiwan
    web site from gitbook

    :copyright: (c) 2016 by chairco <chairco@gmail.com>.
    :license: MIT.
"""

import uuid

from pip.req import parse_requirements  
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand

import vtdiscourse


def requirements(path):  
    return [str(r.req) for r in parse_requirements(path, session=uuid.uuid1())]


class Tox(TestCommand):

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = ['-v', '-epy']
        self.test_suite = True

    def run_tests(self):
        import tox
        tox.cmdline(self.test_args)


setup(  
    name='vtdiscourse',
    version=vtdiscourse.__version__,
    author=vtdiscourse.__author__,
    author_email=vtdiscourse.__email__,
    url='https://github.com/chairco/vtdiscourse',
    description='Help to create topic on talk.vTaiwan web.',
    long_description=__doc__,
    packages=find_packages(),
    install_requires=requirements('requirements.txt'),
    tests_require=['tox'],
    cmdclass={'test': Tox},
    classifiers=[
        'Development Status :: 1 - Planning',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Documentation',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)