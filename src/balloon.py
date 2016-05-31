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
from ucs import *



class Balloon():
    '''
    Balloon format class
    '''
    
    def __init__(self, link, linkmirror, linkcross, ww, ee, nw, nnw, n, nne, ne, nee, e, see, se, sse, s, ssw, sw, sww, w, nww):
        '''
        Constructor
        
        @param  link:str        The \-directional balloon line character
        @param  linkmirror:str  The /-directional balloon line character
        @param  linkcross:str   The /-directional balloon crossing a \-directional ballonon line character
        @param  ww:str          See the info manual
        @param  ee:str          See the info manual
        @param  nw:list<str>    See the info manual
        @param  nnw:list<str>   See the info manual
        @param  n:list<str>     See the info manual
        @param  nne:list<str>   See the info manual
        @param  ne:list<str>    See the info manual
        @param  nee:str         See the info manual
        @param  e:str           See the info manual
        @param  see:str         See the info manual
        @param  se:list<str>    See the info manual
        @param  sse:list<str>   See the info manual
        @param  s:list<str>     See the info manual
        @param  ssw:list<str>   See the info manual
        @param  sw:list<str>    See the info manual
        @param  sww:str         See the info manual
        @param  w:str           See the info manual
        @param  nww:str         See the info manual
        '''
        (self.link, self.linkmirror, self.linkcross) = (link, linkmirror, linkcross)
        (self.ww, self.ee) = (ww, ee)
        (self.nw, self.ne, self.se, self.sw) = (nw, ne, se, sw)
        (self.nnw, self.n, self.nne) = (nnw, n, nne)
        (self.nee, self.e, self.see) = (nee, e, see)
        (self.sse, self.s, self.ssw) = (sse, s, ssw)
        (self.sww, self.w, self.nww) = (sww, w, nww)
        
        _ne = max(ne, key = UCS.dispLen)
        _nw = max(nw, key = UCS.dispLen)
        _se = max(se, key = UCS.dispLen)
        _sw = max(sw, key = UCS.dispLen)
        
        minE = UCS.dispLen(max([_ne, nee, e, see, _se, ee], key = UCS.dispLen))
        minW = UCS.dispLen(max([_nw, nww, e, sww, _sw, ww], key = UCS.dispLen))
        minN = len(max([ne, nne, n, nnw, nw], key = len))
        minS = len(max([se, sse, s, ssw, sw], key = len))
        
        self.minwidth  = minE + minE
        self.minheight = minN + minS
    
    
    def get(self, minw, minh, lines, lencalc):
        '''
        Generates a balloon with a message
        
        @param   minw:int          The minimum number of columns of the balloon
        @param   minh:int          The minimum number of lines of the balloon
        @param   lines:list<str>   The text lines to display
        @param   lencalc:int(str)  Function used to compute the length of a text line
        @return  :str              The balloon as a formated string
        '''
        ## Get dimension
        h = self.minheight + len(lines)
        w = self.minwidth + lencalc(max(lines, key = lencalc))
        if w < minw:  w = minw
        if h < minh:  h = minh
        
        ## Create edges
        if len(lines) > 1:
            (ws, es) = ({0 : self.nww, len(lines) - 1 : self.sww}, {0 : self.nee, len(lines) - 1 : self.see})
            for j in range(1, len(lines) - 1):
                ws[j] = self.w
                es[j] = self.e
        else:
            (ws, es) = ({0 : self.ww}, {0 : self.ee})
        
        rc = []
        
        ## Create the upper part of the balloon
        for j in range(0, len(self.n)):
            outer = UCS.dispLen(self.nw[j]) + UCS.dispLen(self.ne[j])
            inner = UCS.dispLen(self.nnw[j]) + UCS.dispLen(self.nne[j])
            if outer + inner <= w:
                rc.append(self.nw[j] + self.nnw[j] + self.n[j] * (w - outer - inner) + self.nne[j] + self.ne[j])
            else:
                rc.append(self.nw[j] + self.n[j] * (w - outer) + self.ne[j])
        
        ## Encapsulate the message instead left and right edges of balloon
        for j in range(0, len(lines)):
            rc.append(ws[j] + lines[j] + ' ' * (w - lencalc(lines[j]) - UCS.dispLen(self.w) - UCS.dispLen(self.e)) + es[j])
        
        ## Create the lower part of the balloon
        for j in range(0, len(self.s)):
            outer = UCS.dispLen(self.sw[j]) + UCS.dispLen(self.se[j])
            inner = UCS.dispLen(self.ssw[j]) + UCS.dispLen(self.sse[j])
            if outer + inner <= w:
                rc.append(self.sw[j] + self.ssw[j] + self.s[j] * (w - outer - inner) + self.sse[j] + self.se[j])
            else:
                rc.append(self.sw[j] + self.s[j] * (w - outer) + self.se[j])
        
        return '\n'.join(rc)
    
    
    @staticmethod
    def fromFile(balloonfile, isthink):
        '''
        Creates the balloon style object
        
        @param   balloonfile:str  The file with the balloon style, may be `None`
        @param   isthink:bool     Whether the ponythink command is used
        @return  :Balloon         Instance describing the balloon's style
        '''
        ## Use default balloon if none is specified
        if balloonfile is None:
            if isthink:
                return Balloon('o', 'o', 'o', '( ', ' )', [' _'], ['_'], ['_'], ['_'], ['_ '], ' )',  ' )', ' )', ['- '], ['-'], ['-'], ['-'], [' -'],  '( ', '( ', '( ')
            return    Balloon('\\', '/', 'X', '< ', ' >', [' _'], ['_'], ['_'], ['_'], ['_ '], ' \\', ' |', ' /', ['- '], ['-'], ['-'], ['-'], [' -'], '\\ ', '| ', '/ ')
        
        ## Initialise map for balloon parts
        map = {}
        for elem in ('\\', '/', 'X', 'ww', 'ee', 'nw', 'nnw', 'n', 'nne', 'ne', 'nee', 'e', 'see', 'se', 'sse', 's', 'ssw', 'sw', 'sww', 'w', 'nww'):
            map[elem] = []
        
        ## Read all lines in the balloon file
        with open(balloonfile, 'rb') as balloonstream:
            data = balloonstream.read().decode('utf8', 'replace')
            data = [line.replace('\n', '') for line in data.split('\n')]
        
        ## Parse the balloon file, and fill the map
        last = None
        for line in data:
            if len(line) > 0:
                if line[0] == ':':
                    map[last].append(line[1:])
                else:
                    last = line[:line.index(':')]
                    value = line[len(last) + 1:]
                    map[last].append(value)
        
        ## Return the balloon
        return Balloon(map['\\'][0], map['/'][0], map['X'][0], map['ww'][0], map['ee'][0], map['nw'], map['nnw'], map['n'],
                       map['nne'], map['ne'], map['nee'][0], map['e'][0], map['see'][0], map['se'], map['sse'],
                       map['s'], map['ssw'], map['sw'], map['sww'][0], map['w'][0], map['nww'][0])

