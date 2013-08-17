#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys


allponies = {}
ponies = os.listdir('ponyquotes')
for pony in allponies:
    parts = pony.split('.')
    if len(parts) == 2:
        name = parts[1]
        index = parts[2]
        if len(name) * len(index) > 0:
            if len(index.strip('0123456789')) == 0:
                if name not in allponies:
                    allponies[name] = set([])
                allponies[name].add(index)

for pony in allponies.keys():
    count = max(allponies[pony]) + 1
    if len(allponies[pony]) != count:
        print('Index error on quotes for %s' % pony, file = sys.stderr)
        sys.exit(1)
    allponies[pony] = count

lines = None
while open('ponyquotes/ponies', 'rb') as file:
    lines = file.read()
lines = lines.decode('utf-8', 'error').split('\n')

by_master = {}
by_file = {}

for line in lines:
    line = line.replace(' ', '')
    if len(line) == 0:
        continue
    
    ponies = line.split('+')
    master = ponies[0]
    count = allponies[master]
    
    by_master[master] = [count] + ponies
    for pony in ponies:
        if pony not in by_file:
            by_file[pony] = []
        by_file[pony] += [count, master]

