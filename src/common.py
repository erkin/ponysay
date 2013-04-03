#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
ponysay - Ponysay, cowsay reimplementation for ponies

Copyright (C) 2012, 2013  Erkin Batu Altunbaş et al.


This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.


If you intend to redistribute ponysay or a fork of it commercially,
it contains aggregated images, some of which may not be commercially
redistribute, you would be required to remove those. To determine
whether or not you may commercially redistribute an image make use
that line ‘FREE: yes’, is included inside the image between two ‘$$$’
lines and the ‘FREE’ is and upper case and directly followed by
the colon.
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

