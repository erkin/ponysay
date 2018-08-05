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



class UCS():
    '''
    UCS utility class
    '''
    
    @staticmethod
    def isCombining(char):
        '''
        Checks whether a character is a combining character
        
        @param   char:chr  The character to test
        @return  :bool     Whether the character is a combining character
        '''
        o = ord(char)
        if (0x0300 <= o) and (o <= 0x036F):  return True
        if (0x20D0 <= o) and (o <= 0x20FF):  return True
        if (0x1DC0 <= o) and (o <= 0x1DFF):  return True
        if (0xFE20 <= o) and (o <= 0xFE2F):  return True
        return False
    
    
    @staticmethod
    def countCombining(string):
        '''
        Gets the number of combining characters in a string
        
        @param   string:str  A text to count combining characters in
        @return  :int        The number of combining characters in the string
        '''
        rc = 0
        for char in string:
            if UCS.isCombining(char):
                rc += 1
        return rc
    
    
    @staticmethod
    def dispLen(string):
        '''
        Gets length of a string not counting combining characters
        
        @param   string:str  The text of which to determine the monospaced width
        @return              The determine the monospaced width of the text, provided it does not have escape sequnces
        '''
        return len(string) - UCS.countCombining(string)

