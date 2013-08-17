#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import dbm


allponies = {}
ponies = os.listdir('ponyquotes')
for pony in ponies:
    parts = pony.split('.')
    if len(parts) == 2:
        name = parts[0]
        index = parts[1]
        if len(name) * len(index) > 0:
            if len(index.strip('0123456789')) == 0:
                if name not in allponies:
                    allponies[name] = set([])
                allponies[name].add(int(index))

for pony in allponies.keys():
    count = max(allponies[pony]) + 1
    if len(allponies[pony]) != count:
        print('Index error on quotes for %s' % pony, file = sys.stderr)
        sys.exit(1)
    allponies[pony] = str(count)

masters = {}
ponies = os.listdir('ponies')
for pony in ponies:
    if pony.endswith('.pony') and (len(pony) > 5):
        name = pony[:-5]
        pony = 'ponies/' + pony
        data = None
        with open(pony, 'rb') as file:
            data = file.read()
        data = data.decode('utf-8', 'error')
        if not data.startswith('$$$\n'):
            print('%s as no metadata' % pony, file = sys.stderr)
            sys.exit(1)
        data = data[3:]
        data = data[:data.index('$$$\n')]
        if '\n\n' in data:
            data = data[:data.index('\n\n')]
        master = name
        if '\nMASTER:' in data:
            master = data[data.index('\nMASTER:') + 9:] + '\n'
            master = data[:data.index('\n')]
            master = master.strip()
        if master not in masters:
            masters[master] = []
        masters[master].append(name)

by_master = {}
by_file = {}

for master in masters:
    ponies = masters[master]
    if master not in allponies:
        continue
    count = allponies[master]
    
    by_master[master] = [count] + ponies
    for pony in ponies:
        if pony not in by_file:
            by_file[pony] = []
        by_file[pony] += [count, master]

db = dbm.open('by-master', 'n')
for key in by_master:
    db[key] = ' '.join(by_master[key])
db.close()

db = dbm.open('by-file', 'n')
for key in by_file:
    db[key] = ' '.join(by_file[key])
db.close()

