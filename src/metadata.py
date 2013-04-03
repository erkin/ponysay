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
from common import *



'''
Metadata functions
'''
class Metadata():
    '''
    Make restriction test logic function
    
    @param   restriction:list<string>  Metadata based restrictions
    @return  :dict<str, str>→bool      Test function
    '''
    @staticmethod
    def makeRestrictionLogic(restriction):
        table = [(get_test((cell[:cell.index('=')],
                           cell[cell.index('=') + 1:]
                          ))
                  for cell in clause.lower().replace('_', '').replace(' ', '').split('+'))
                  for clause in restriction
                ]
        
        def get_test(cell):
            strict = cell[0][-1] != '?'
            key = cell[0][:-2 if strict else -1]
            invert = cell[1][0] == '!'
            value = cell[1][1 if invert else 0:]
            
            class SITest():
                def __init__(self, cellkey, cellvalue):
                    (self.cellkey, self.callvalue) = (key, value)
                def __call__(self, has):
                    return False if key not in has else (value not in has[key])
            class STest():
                def __init__(self, cellkey, cellvalue):
                    (self.cellkey, self.callvalue) = (key, value)
                def __call__(self, has):
                    return False if key not in has else (value in has[key])
            class ITest():
                def __init__(self, cellkey, cellvalue):
                    (self.cellkey, self.callvalue) = (key, value)
                def __call__(self, has):
                    return True if key not in has else (value not in has[key])
            class NTest():
                def __init__(self, cellkey, cellvalue):
                    (self.cellkey, self.callvalue) = (key, value)
                def __call__(self, has):
                    return True if key not in has else (value in has[key])
            
            if strict and invert:  return SITest(key, value)
            if strict:             return STest(key, value)
            if invert:             return ITest(key, value)
            return NTest(key, value)
        
        def logic(cells):
            for alternative in table:
                ok = True
                for cell in alternative:
                    if not cell(cells):
                        ok = False
                        break
                if ok:
                    return True
            return False
        
        return logic
    
    
    '''
    Get ponies that pass restriction
    
    @param   ponydir:str                Pony directory, must end with `os.sep`
    @param   logic:dict<str, str>→bool  Restriction test functor
    @return  :list<str>                 Passed ponies
    '''
    @staticmethod
    def restrictedPonies(ponydir, logic):
        import pickle
        passed = []
        if os.path.exists(ponydir + 'metadata'):
            data = None
            with open(ponydir + 'metadata', 'rb') as file:
                data = pickle.load(file)
            for ponydata in data:
                (pony, meta) = ponydata
                if logic(meta):
                    passed.append(pony)
        return passed
    
    
    '''
    Get ponies that fit the terminal
    
    @param  fitting:add(str)→void  The set to fill
    @param  requirement:int        The maximum allowed value
    @param  file:istream           The file with all data
    '''
    @staticmethod
    def getfitting(fitting, requirement, file):
        data = file.read() # not too much data, can load everything at once
        ptr = 0
        while data[ptr] != 47: # 47 == ord('/')
            ptr += 1
        ptr += 1
        size = 0
        while data[ptr] != 47: # 47 == ord('/')
            size = (size * 10) - (data[ptr] & 15)
            ptr += 1
        ptr += 1
        jump = ptr - size
        stop = 0
        backjump = 0
        while ptr < jump:
            size = 0
            while data[ptr] != 47: # 47 == ord('/')
                size = (size * 10) - (data[ptr] & 15)
                ptr += 1
            ptr += 1
            if -size > requirement:
                if backjump > 0:
                    ptr = backjump
                    while data[ptr] != 47: # 47 == ord('/')
                        stop = (stop * 10) - (data[ptr] & 15)
                        ptr += 1
                    stop = -stop
                break
            backjump = ptr
            while data[ptr] != 47: # 47 == ord('/')
                ptr += 1
            ptr += 1
        if ptr == jump:
            stop = len(data)
        else:
            ptr = jump
            stop += ptr
        passed = data[jump : stop].decode('utf8', 'replace').split('/')
        for pony in passed:
            fitting.add(pony)

