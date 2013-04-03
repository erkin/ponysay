#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
ponysay - Ponysay, cowsay reimplementation for ponies
Copyright (C) 2012, 2013  Erkin Batu Altunbaş et al.

This program is free software. It comes without any warranty, to
the extent permitted by applicable law. You can redistribute it
and/or modify it under the terms of the Do What The Fuck You Want
To Public License, Version 2, as published by Sam Hocevar. See
http://sam.zoy.org/wtfpl/COPYING for more details.
'''

import os
import shutil
import sys
import random
from subprocess import Popen, PIPE



'''
The version of ponysay
'''
VERSION = 'dev'  # this line should not be edited, it is fixed by the build system



'''
Hack to enforce UTF-8 in output (in the future, if you see anypony not using utf-8 in
programs by default, report them to Princess Celestia so she can banish them to the moon)

@param  text:str  The text to print (empty string is default)
@param  end:str   The appendix to the text to print (line breaking is default)
'''
def print(text = '', end = '\n'):
    sys.stdout.buffer.write((str(text) + end).encode('utf-8'))

'''
stderr equivalent to print()

@param  text:str  The text to print (empty string is default)
@param  end:str   The appendix to the text to print (line breaking is default)
'''
def printerr(text = '', end = '\n'):
    sys.stderr.buffer.write((str(text) + end).encode('utf-8'))

fd3 = None
'''
/proc/self/fd/3 equivalent to print()

@param  text:str  The text to print (empty string is default)
@param  end:str   The appendix to the text to print (line breaking is default)
'''
def printinfo(text = '', end = '\n'):
    global fd3
    if os.path.exists('/proc/self/fd/3') and os.path.isfile('/proc/self/fd/3'):
        if fd3 is None:
            fd3 = os.fdopen(3, 'w')
    if fd3 is not None:
        fd3.write(str(text) + end)


'''
Checks whether a text ends with a specific text, but has more

@param   text:str    The text to test
@param   ending:str  The desired end of the text
@return  :bool       The result of the test
'''
def endswith(text, ending):
    return text.endswith(ending) and not (text == ending)


'''
Gets the size of the terminal in (rows, columns)

@return  (rows, columns):(int, int)  The number or lines and the number of columns in the terminal's display area
'''
def gettermsize():
    ## Call `stty` to determine the size of the terminal, this way is better than using python's ncurses
    for channel in (sys.stderr, sys.stdout, sys.stdin):
        termsize = Popen(['stty', 'size'], stdout=PIPE, stdin=channel, stderr=PIPE).communicate()[0]
        if len(termsize) > 0:
            termsize = termsize.decode('utf8', 'replace')[:-1].split(' ') # [:-1] removes a \n
            termsize = [int(item) for item in termsize]
            return termsize
    return (24, 80) # fall back to minimal sane size

