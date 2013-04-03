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
from common import *



'''
UCS utility class
'''
class UCS():
    '''
    Checks whether a character is a combining character
    
    @param   char:chr  The character to test
    @return  :bool     Whether the character is a combining character
    '''
    @staticmethod
    def isCombining(char):
        o = ord(char)
        if (0x0300 <= o) and (o <= 0x036F):  return True
        if (0x20D0 <= o) and (o <= 0x20FF):  return True
        if (0x1DC0 <= o) and (o <= 0x1DFF):  return True
        if (0xFE20 <= o) and (o <= 0xFE2F):  return True
        return False
    
    
    '''
    Gets the number of combining characters in a string
    
    @param   string:str  A text to count combining characters in
    @return  :int        The number of combining characters in the string
    '''
    @staticmethod
    def countCombining(string):
        rc = 0
        for char in string:
            if UCS.isCombining(char):
                rc += 1
        return rc
    
    
    '''
    Gets length of a string not counting combining characters
    
    @param   string:str  The text of which to determine the monospaced width
    @return              The determine the monospaced width of the text, provided it does not have escape sequnces
    '''
    @staticmethod
    def dispLen(string):
        return len(string) - UCS.countCombining(string)

