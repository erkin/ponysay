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



class SpelloCorrecter(): # Naïvely and quickly ported and adapted from optimised Java, may not be the nicest, or even fast, Python code
    '''
    Class used for correcting spellos and typos,
    
    Note that this implementation will not find that correctly spelled word are correct faster than it corrects words.
    It is also limited to words of size 0 to 127 (inclusive)
    '''
    
    def __init__(self, directories, ending = None):
        '''
        Constructor
        
        @param  directories:list<str>  List of directories that contains the file names with the correct spelling
        @param  ending:str             The file name ending of the correctly spelled file names, this is removed for the name
        
        -- OR -- (emulated overloading [overloading is absent in Python])
        
        @param  directories:list<str>  The file names with the correct spelling
        '''
        self.weights = {'k' : {'c' : 0.25, 'g' : 0.75, 'q' : 0.125},
                        'c' : {'k' : 0.25, 'g' : 0.75, 's' : 0.5, 'z' : 0.5, 'q' : 0.125},
                        's' : {'z' : 0.25, 'c' : 0.5},
                        'z' : {'s' : 0.25, 'c' : 0.5},
                        'g' : {'k' : 0.75, 'c' : 0.75, 'q' : 0.9},
                        'o' : {'u' : 0.5},
                        'u' : {'o' : 0.5, 'v' : 0.75, 'w' : 0.5},
                        'b' : {'v' : 0.75},
                        'v' : {'b' : 0.75, 'w' : 0.5, 'u' : 0.7},
                        'w' : {'v' : 0.5, 'u' : 0.5},
                        'q' : {'c' : 0.125, 'k' : 0.125, 'g' : 0.9}}
        
        self.corrections = None
        self.dictionary = [None] * 513
        self.reusable = [0] * 512
        self.dictionaryEnd = 512
        self.closestDistance = 0
        
        self.M = [None] * 128
        for y in range(0, 128):
            self.M[y] = [0] * 128
            self.M[y][0] = y
        m0 = self.M[0]
        x = 127
        while x > -1:
            m0[x] = x
            x -= 1
        
        previous = ''
        self.dictionary[-1] = previous;
        
        if ending is not None:
            for directory in directories:
                files = os.listdir(directory)
                files.sort()
                for filename in files:
                    if (not endswith(filename, ending)) or (len(filename) - len(ending) > 127):
                        continue
                    proper = filename[:-len(ending)]
                    
                    if self.dictionaryEnd == 0:
                        self.dictionaryEnd = len(self.dictionary)
                        self.reusable = [0] * self.dictionaryEnd + self.reusable
                        self.dictionary = [None] * self.dictionaryEnd + self.dictionary
                    
                    self.dictionaryEnd -= 1
                    self.dictionary[self.dictionaryEnd] = proper
                    
                    prevCommon = min(len(previous), len(proper))
                    for i in range(0, prevCommon):
                        if previous[i] != proper[i]:
                            prevCommon = i
                            break
                    previous = proper
                    self.reusable[self.dictionaryEnd] = prevCommon
        else:
            files = directories
            files.sort()
            for proper in files:
                if len(proper) > 127:
                    continue
                
                if self.dictionaryEnd == 0:
                    self.dictionaryEnd = len(self.dictionary)
                    self.reusable = [0] * self.dictionaryEnd + self.reusable
                    self.dictionary = [None] * self.dictionaryEnd + self.dictionary
                
                self.dictionaryEnd -= 1
                self.dictionary[self.dictionaryEnd] = proper
                
                prevCommon = min(len(previous), len(proper))
                for i in range(0, prevCommon):
                    if previous[i] != proper[i]:
                        prevCommon = i
                        break
                previous = proper
                self.reusable[self.dictionaryEnd] = prevCommon
        #part = self.dictionary[self.dictionaryEnd : len(self.dictionary) - 1]
        #part.sort()
        #self.dictionary[self.dictionaryEnd : len(self.dictionary) - 1] = part
        #
        #index = len(self.dictionary) - 1
        #while index >= self.dictionaryEnd:
        #    proper = self.dictionary[index]
        #    prevCommon = min(len(previous), len(proper))
        #    for i in range(0, prevCommon):
        #        if previous[i] != proper[i]:
        #            prevCommon = i
        #            break
        #    previous = proper
        #    self.reusable[self.dictionaryEnd] = prevCommon
        #    index -= 1;    
    
    
    def correct(self, used):
        '''
        Finds the closests correct spelled word
        
        @param   used:str                               The word to correct
        @return  (words, distance):(list<string>, int)  A list the closest spellings and the weighted distance
        '''
        if len(used) > 127:
            return ([used], 0)
        
        self.__correct(used)
        return (self.corrections, self.closestDistance)
    
    
    def __correct(self, used):
        '''
        Finds the closests correct spelled word
        
        @param  used:str  The word to correct, it must satisfy all restrictions
        '''
        self.closestDistance = 0x7FFFFFFF
        previous = self.dictionary[-1]
        prevLen = 0
        usedLen = len(used)
        
        proper = None
        prevCommon = 0
        
        d = len(self.dictionary) - 1
        while d > self.dictionaryEnd:
            d -= 1
            proper = self.dictionary[d]
            if abs(len(proper) - usedLen) <= self.closestDistance:
                if previous == self.dictionary[d + 1]:
                    prevCommon = self.reusable[d];
                else:
                    prevCommon = min(prevLen, len(proper))
                    for i in range(0, prevCommon):
                        if previous[i] != proper[i]:
                            prevCommon = i
                            break
                
                skip = min(prevLen, len(proper))
                i = prevCommon
                while i < skip:
                    for u in range(0, usedLen):
                        if (used[u] == previous[i]) or (used[u] == proper[i]):
                            skip = i
                            break
                    i += 1
                
                common = min(skip, min(usedLen, len(proper)))
                for i in range(0, common):
                    if used[i] != proper[i]:
                        common = i
                        break
                
                distance = self.__distance(proper, skip, len(proper), used, common, usedLen)
                
                if self.closestDistance > distance:
                    self.closestDistance = distance
                    self.corrections = [proper]
                elif self.closestDistance == distance:
                    self.corrections.append(proper)
                
                previous = proper;
                if distance >= 0x7FFFFF00:
                    prevLen = distance & 255
                else:
                    prevLen = len(proper)
    
    
    def __distance(self, proper, y0, yn, used, x0, xn):
        '''
        Calculate the distance between a correct word and a incorrect word
        
        @param   proper:str  The correct word
        @param   y0:int      The offset for `proper`
        @param   yn:int      The length, before applying `y0`, of `proper`
        @param   used:str    The incorrect word
        @param   x0:int      The offset for `used`
        @param   xn:int      The length, before applying `x0`, of `used`
        @return  :float      The distance between the words
        '''
        my = self.M[y0]
        for y in range(y0, yn):
            best = 0x7FFFFFFF
            p = proper[y]
            myy = self.M[y + 1] # only one array bound check, and at most one + ☺
            x = x0
            while x < xn:
                change = my[x]
                u = used[x]
                remove = myy[x]
                add = my[x + 1]
                
                cw = 0 if p == u else 1
                if my[x] in self.weights:
                    if p in self.weights[u]:
                      cw = self.weights[u][p]
                x += 1
                
                myy[x] = min(cw + change, 1 + min(remove, add))
                if best > myy[x]:
                    best = myy[x]
            
            if best > self.closestDistance:
                return 0x7FFFFF00 | y
            my = myy
        
        return my[xn]

