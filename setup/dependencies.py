#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

dependencies = [
    ('chmod',              'coreutils',             None,                                  2, 1),
    ('gzip',               'gzip',                  'compression of manuals',              1, 0),
    ('makeinfo',           'texinfo',               'compilation of info manual',          1, 0),
    ('install-info',       'texinfo',               'installation of info manual',         1, 0),
    ('auto-auto-complete', 'auto-auto-complete>=3', 'compilation of shell tab-completion', 1, 0),
    ('stty',               'coreutils',             None,                                  0, 2),
    ('ponytool',           'util-say>=3',           'KMS utilisation and PNG support',     0, 1),
    (None,                 'python>=3',             None,                                  2, 2)
]

path = os.environ['PATH'].split(':')

build_required = True
build_optional = True
runtime_required = True
runtime_optional = True

def test(dependency):
    executable = dependency[0]
    if executable is None:
        if sys.version_info.major == 3:
            return
        executable = 'python3'
    for p in path:
        if len(p) != 0:
            if os.path.exists((p + '/' + executable).replace('//', '/')):
                return
    global build_required, build_optional, runtime_required, runtime_optional
    requirement = ''
    if dependency[3] == 2:    build_required = False ; requirement += 'build required + '
    if dependency[3] == 1:    build_optional = False ; requirement += 'build optional + '
    if dependency[4] == 2:  runtime_required = False ; requirement += 'runtime required + '
    if dependency[4] == 1:  runtime_optional = False ; requirement += 'runtime optional + '
    requirement = requirement[:len(requirement) - 3]
    print('Missing %s, install %s. [%s]' % (executable, dependency[1], requirement))
    if dependency[2] is not None:
        print('  Required for %s.' % dependency[2])

for dependency in dependencies:
    test(dependency)

rc = 0

if not build_required:
    print('You will not be able to build and install ponysay.')
    rc = 1
elif not build_optional:
    print('You will have to tweak to installation to build and install ponysay.')

if not runtime_required:
    print('You will not be able to run ponysay.')
    rc = 1
elif not runtime_optional:
    print('You will be missing some features in ponysay.')

if not (build_required and build_optional and runtime_required and runtime_optional):
    print('\nEverything appears to be in order, enjoy ponysay!')

exit(rc)

