#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Pipe the content of a pony file to this script to make the printed
# information easier to read. This is intended for inspection pony
# files in greater detail than using it in ponysay.


comment = False
while True:
    line = None
    try:
        line = input()
    except:
        pass
    if line is None:
        break
    if line == '$$$':
        comment = not comment
        continue
    if comment:
        continue
    line = line.replace('$\\$', '\\').replace('$/$', '/').replace('$X$', 'X');
    if line.startswith('$balloon'):
        line = line[len('$balloon'):]
        balloon = line[:line.find('$')]
        line = line[len(balloon) + 1:]
        for alpha in 'qwertyuiopasdfghjklzxcvbnm':
            balloon = balloon.replace(alpha, ',')
        balloon = balloon.split(',')[0]
        if len(balloon) == 0:
            line = '\033[01;33;41m%s\033[00m' % (50 * '/') + line
        else:
            line = '\033[42m%s\033[00m' % (int(balloon) * ' ') + line
    print(line)


