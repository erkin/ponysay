#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
from subprocess import Popen


def generateTTY(ponydir, ttyponydir, judge):
    if    ponydir.endswith('/'):    ponydir =    ponydir[:-1]
    if ttyponydir.endswith('/'): ttyponydir = ttyponydir[:-1]
    
    defaultinparams = '--left - --right - --top - --bottom -'.split(' ')
    defaultoutparams = '--colourful y --left - --right - --top - --bottom - --balloon n --fullcolour y'.split(' ')
    
    os.makedirs(ttyponydir, Oo755, True)
    for pony in os.listdir(ponydir):
        infile  = '%s/%s' % (   ponydir, pony)
        outfile = '%s/%s' % (ttyponydir, pony)
        if (not pony.endswith('.pony')) or (len(pony) <= 5) or not judge(infile):
            continue
        print('Building %s' % outfile)
        if os.path.islink(infile):
            os.symlink(os.readlink(infile), outfile)
        else:
            cmd = ['ponytool', '--import', 'ponysay', '--file', infile] + defaultinparams
            cmd += ['--export', 'ponysay', '--platform', 'linux', '--file', outfile] + defaultoutparams
            Popen(cmd, stdin = sys.stdin, stdout = sys.stdout, stderr = sys.stderr)


if __name__ == '__main__':
    generateTTY(sys.args[1], sys.args[1], lambda _ : True)

