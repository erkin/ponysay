#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
ponysay - Ponysay, cowsay reimplementation for ponies

Copyright (C) 2012-2016  Erkin Batu Altunbaş et al.


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

import fcntl
import os
import struct
import sys
import termios



VERSION = 'dev'  # this line should not be edited, it is fixed by the build system
'''
The version of ponysay
'''



def print(text = '', end = '\n'):
    '''
    Hack to enforce UTF-8 in output (in the future, if you see anypony not using utf-8 in
    programs by default, report them to Princess Celestia so she can banish them to the moon)
    
    @param  text:str  The text to print (empty string is default)
    @param  end:str   The appendix to the text to print (line breaking is default)
    '''
    sys.stdout.buffer.write((str(text) + end).encode('utf-8'))

def printerr(text = '', end = '\n'):
    '''
    stderr equivalent to print()
    
    @param  text:str  The text to print (empty string is default)
    @param  end:str   The appendix to the text to print (line breaking is default)
    '''
    sys.stderr.buffer.write((str(text) + end).encode('utf-8'))

fd3 = None
def printinfo(text = '', end = '\n'):
    '''
    /proc/self/fd/3 equivalent to print()
    
    @param  text:str  The text to print (empty string is default)
    @param  end:str   The appendix to the text to print (line breaking is default)
    '''
    global fd3
    if os.path.exists('/proc/self/fd/3') and not os.path.isdir(os.path.realpath('/proc/self/fd/3')):
        if fd3 is None:
            fd3 = os.fdopen(3, 'w')
    if fd3 is not None:
        fd3.write(str(text) + end)


def endswith(text, ending):
    '''
    Checks whether a text ends with a specific text, but has more
    
    @param   text:str    The text to test
    @param   ending:str  The desired end of the text
    @return  :bool       The result of the test
    '''
    return text.endswith(ending) and not (text == ending)


def gettermsize():
    '''
    Gets the size of the terminal in (rows, columns)
    
    @return  (rows, columns):(int, int)  The number or lines and the number of columns in the terminal's display area
    '''
    try:
        size = bytearray(struct.pack("HHHH",0,0,0,0))
        fcntl.ioctl(0,termios.TIOCGWINSZ,size)
        r,c,_,_ = struct.unpack("HHHH",size)
        return (r,c)
    except:
        return (24,80)

