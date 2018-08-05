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
from common import *



class ColourStack():
    '''
    ANSI colour stack
    
    This is used to make layers with independent coloursations
    '''
    
    def __init__(self, autopush, autopop):
        '''
        Constructor
        
        @param  autopush:str  String that, when used, will create a new independently colourised layer
        @param  autopop:str   String that, when used, will end the current layer and continue of the previous layer
        '''
        self.autopush = autopush
        self.autopop  = autopop
        self.lenpush  = len(autopush)
        self.lenpop   = len(autopop)
        self.bufproto = ' ' * (self.lenpush if self.lenpush > self.lenpop else self.lenpop)
        self.stack    = []
        self.push()
        self.seq      = None
    
    
    def push(self):
        '''
        Create a new independently colourised layer
        
        @return  :str  String that should be inserted into your buffer
        '''
        self.stack.insert(0, [self.bufproto, None, None, [False] * 9])
        if len(self.stack) == 1:
            return None
        return '\033[0m'
    
    
    def pop(self):
        '''
        End the current layer and continue of the previous layer
        
        @return  :str  String that should be inserted into your buffer
        '''
        old = self.stack.pop(0)
        rc = '\033[0;'
        if len(self.stack) == 0: # last resort in case something made it pop too mush
            push()
        new = self.stack[0]
        if new[1] is not None:  rc += new[1] + ';'
        if new[2] is not None:  rc += new[2] + ';'
        for i in range(0, 9):
            if new[3][i]:
                rc += str(i + 1) + ';'
        return rc[:-1] + 'm'
    
    
    def feed(self, char):
        '''
        Use this, in sequence, for which character in your buffer that contains yor autopush and autopop
        string, the automatically get push and pop string to insert after each character
        
        @param   :chr  One character in your buffer
        @return  :str  The text to insert after the input character
        '''
        if self.seq is not None:
            self.seq += char
            if (char == '~') or (('a' <= char) and (char <= 'z')) or (('A' <= char) and (char <= 'Z')):
                if (self.seq[0] == '[') and (self.seq[-1] == 'm'):
                    self.seq = self.seq[1:-1].split(';')
                    (i, n) = (0, len(self.seq))
                    while i < n:
                        part = self.seq[i]
                        p = 0 if part == '' else int(part)
                        i += 1
                        if p == 0:             self.stack[0][1:] = [None, None, [False] * 9]
                        elif 1 <= p <= 9:      self.stack[0][3][p - 1] = True
                        elif 21 <= p <= 29:    self.stack[0][3][p - 21] = False
                        elif p == 39:          self.stack[0][1] = None
                        elif p == 49:          self.stack[0][2] = None
                        elif 30 <= p <= 37:    self.stack[0][1] = part
                        elif 90 <= p <= 97:    self.stack[0][1] = part
                        elif 40 <= p <= 47:    self.stack[0][2] = part
                        elif 100 <= p <= 107:  self.stack[0][2] = part
                        elif p == 38:
                            self.stack[0][1] = '%s;%s;%s' % (part, self.seq[i], self.seq[i + 1])
                            i += 2
                        elif p == 48:
                            self.stack[0][2] = '%s;%s;%s' % (part, self.seq[i], self.seq[i + 1])
                            i += 2
                self.seq = None
        elif char == '\033':
            self.seq = ''
        buf = self.stack[0][0]
        buf = buf[1:] + char
        rc = ''
        if   buf[-self.lenpush:] == self.autopush:  rc = self.push()
        elif buf[-self.lenpop:]  == self.autopop:   rc = self.pop()
        self.stack[0][0] = buf
        return rc

