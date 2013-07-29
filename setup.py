#!/usr/bin/env python3
import distutils.core
from setuptools import setup
import subprocess
import os, os.path
import sys

ver = "1.0"

def read(filename):
    return open(os.path.join(os.path.dirname(__file__), filename)).read()

def dir_copy(src, dst):
	return (dst, [src+'/'+f for f in os.listdir(src)])


if sys.version_info < (3,0):
    print('Oops, only python >= 3.0 supported!')
    sys.exit()

subprocess.call('make', cwd=os.path.realpath(os.path.dirname(__file__)))

setup(name = 'ponysay',
    version = ver,
    description = 'cowsay with ponies',
    license = 'WTFPL',
    author = 'jaseg',
    author_email = 'ponysay@jaseg.net',
    url = 'https://github.com/jaseg/ponysay',
	py_modules = ['ponysay'],
	data_files = [dir_copy('quotes', 'ponies'),
				  dir_copy('genponies', 'ponies')],
    scripts = ['ponysay',
			   'ponythink',
			   'termcenter',
               'ponysay-qotd'],
    zip_safe = False,
    classifiers = [
		'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Information Technology',
		'Intended Audience :: Intended Audience :: End Users/Desktop',
		'License :: Freely Distributable',
		'License :: Public Domain',
		'Natural Language :: English',
        'Programming Language :: Python :: 3',
		'Topic :: Games/Entertainment',
		'Topic :: Internet',
        'Topic :: System :: Networking'
		'Topic :: Text Processing :: Filters',
		'Topic :: Utilities',
    ],
    long_description = read('README.md'),
    dependency_links = [],
)
