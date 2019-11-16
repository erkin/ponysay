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
from balloon import *
from colourstack import *
from ucs import *

import unicodedata



class Backend():
    '''
    Super-ultra-extreme-awesomazing replacement for cowsay
    '''
    
    def __init__(self, message, ponyfile, wrapcolumn, width, balloon, hyphen, linkcolour, ballooncolour, mode, infolevel):
        '''
        Constructor
        
        @param  message:str        The message spoken by the pony
        @param  ponyfile:str       The pony file
        @param  wrapcolumn:int     The column at where to wrap the message, `None` for no wrapping
        @param  width:int          The width of the screen, `None` if truncation should not be applied
        @param  balloon:Balloon    The balloon style object, `None` if only the pony should be printed
        @param  hyphen:str         How hyphens added by the wordwrapper should be printed
        @param  linkcolour:str     How to colour the link character, empty string if none
        @param  ballooncolour:str  How to colour the balloon, empty string if none
        @param  mode:str           Mode string for the pony
        @parma  infolevel:int      2 if ++info is used, 1 if --info is used and 0 otherwise
        '''
        self.message = message
        self.ponyfile = ponyfile
        self.wrapcolumn = None if wrapcolumn is None else wrapcolumn - (0 if balloon is None else balloon.minwidth)
        self.width = width
        self.balloon = balloon
        self.hyphen = hyphen
        self.ballooncolour = ballooncolour
        self.mode = mode
        self.balloontop = 0
        self.balloonbottom = 0
        self.infolevel = infolevel
        
        if self.balloon is not None:
            self.link = {'\\' : linkcolour + self.balloon.link,
                         '/'  : linkcolour + self.balloon.linkmirror,
                         'X'  : linkcolour + self.balloon.linkcross}
        else:
            self.link = {}
        
        self.output = ''
        self.pony = None
    
    
    def parse(self):
        '''
        Process all data
        '''
        self.__loadFile()
        
        if self.pony.startswith('$$$\n'):
            self.pony = self.pony[4:]
            if self.pony.startswith('$$$\n'):
                infoend = 4
                info = ''
            else:
                infoend = self.pony.index('\n$$$\n')
                info = self.pony[:infoend]
                infoend += 5
            if self.infolevel == 2:
                self.message = Backend.formatInfo(info)
                self.pony = self.pony[infoend:]
            elif self.infolevel == 1:
                self.pony = Backend.formatInfo(info).replace('$', '$$')
            else:
                info = info.split('\n')
                for line in info:
                    sep = line.find(':')
                    if sep > 0:
                        key = line[:sep].strip()
                        if key == 'BALLOON TOP':
                            value = line[sep + 1:].strip()
                            if len(value) > 0:
                                self.balloontop = int(value)
                        if key == 'BALLOON BOTTOM':
                            value = line[sep + 1:].strip()
                            if len(value) > 0:
                                self.balloonbottom = int(value)
                printinfo(info)
                self.pony = self.pony[infoend:]
        elif self.infolevel == 2:
            self.message = '\033[01;31mI am the mysterious mare...\033[21;39m'
        elif self.infolevel == 1:
            self.pony = 'There is not metadata for this pony file'
        self.pony = self.mode + self.pony
        
        self.__expandMessage()
        self.__unpadMessage()
        self.__processPony()
        self.__truncate()
    
    
    @staticmethod
    def formatInfo(info):
        '''
        Format metadata to be nicely printed, this include bold keys
        
        @param   info:str  The metadata
        @return  :str      The metadata nicely formated
        '''
        info = info.split('\n')
        tags = ''
        comment = ''
        for line in info:
            sep = line.find(':')
            if sep > 0:
                key = line[:sep]
                test = key
                for c in 'ABCDEFGHIJKLMN OPQRSTUVWXYZ':
                    test = test.replace(c, '')
                if (len(test) == 0) and (len(key.replace(' ', '')) > 0):
                    value = line[sep + 1:].strip()
                    line = '\033[1m%s\033[21m: %s\n' % (key.strip(), value)
                    tags += line
                    continue
            comment += '\n' + line
        comment = comment.lstrip('\n')
        if len(comment) > 0:
            comment = '\n' + comment
        return tags + comment
    
    
    def __unpadMessage(self):
        '''
        Remove padding spaces fortune cookies are padded with whitespace (damn featherbrains)
        '''
        lines = self.message.split('\n')
        for spaces in (128, 64, 32, 16, 8, 4, 2, 1):
            padded = True
            for line in lines:
                if not line.startswith(' ' * spaces):
                    padded = False
                    break
            if padded:
                for i in range(0, len(lines)):
                    line = lines[i]
                    line = line[spaces:]
                    lines[i] = line
        lines = [line.rstrip(' ') for line in lines]
        self.message = '\n'.join(lines)
    
    
    def __expandMessage(self):
        '''
        Converts all tabs in the message to spaces by expanding
        '''
        lines = self.message.split('\n')
        buf = ''
        for line in lines:
            (i, n, x) = (0, len(line), 0)
            while i < n:
                c = line[i]
                i += 1
                if c == '\033':
                    colour = Backend.getColour(line, i - 1)
                    i += len(colour) - 1
                    buf += colour
                elif c == '\t':
                    nx = 8 - (x & 7)
                    buf += ' ' * nx
                    x += nx
                else:
                    buf += c
                    if not UCS.isCombining(c):
                        x += 1
            buf += '\n'
        self.message = buf[:-1]
    
    
    def __loadFile(self):
        '''
        Loads the pony file
        '''
        with open(self.ponyfile, 'rb') as ponystream:
            self.pony = ponystream.read().decode('utf8', 'replace')
    
    
    def __truncate(self):
        '''
        Truncate output to the width of the screen
        '''
        if self.width is None:
            return
        lines = self.output.split('\n')
        self.output = ''
        for line in lines:
            (i, n, x) = (0, len(line), 0)
            while i < n:
                c = line[i]
                i += 1
                if c == '\033':
                    colour = Backend.getColour(line, i - 1)
                    i += len(colour) - 1
                    self.output += colour
                else:
                    if x < self.width:
                        self.output += c
                        if not UCS.isCombining(c):
                            x += 1
            self.output += '\n'
        self.output = self.output[:-1]
    
    
    def __processPony(self):
        '''
        Process the pony file and generate output to self.output
        '''
        self.output = ''
        
        AUTO_PUSH = '\033[01010~'
        AUTO_POP  = '\033[10101~'
        
        variables = {'' : '$'}
        for key in self.link:
            variables[key] = AUTO_PUSH + self.link[key] + AUTO_POP
        
        indent = 0
        dollar = None
        balloonLines = None
        colourstack = ColourStack(AUTO_PUSH, AUTO_POP)
        
        (i, n, lineindex, skip, nonskip) = (0, len(self.pony), 0, 0, 0)
        while i < n:
            c = self.pony[i]
            if c == '\t':
                n += 7 - (indent & 7)
                ed = ' ' * (8 - (indent & 7))
                c = ' '
                self.pony = self.pony[:i] + ed + self.pony[i + 1:]
            i += 1
            if c == '$':
                if dollar is not None:
                    if '=' in dollar:
                        name = dollar[:dollar.find('=')]
                        value = dollar[dollar.find('=') + 1:]
                        variables[name] = value
                    elif not dollar.startswith('balloon'):
                        data = variables[dollar].replace('$', '$$')
                        if data == '$$': # if not handled specially we will get an infinity loop
                            if (skip == 0) or (nonskip > 0):
                                if nonskip > 0:
                                    nonskip -= 1
                                self.output += '$'
                                indent += 1
                            else:
                                skip -= 1
                        else:
                            n += len(data)
                            self.pony = self.pony[:i] + data + self.pony[i:]
                    elif self.balloon is not None:
                        (w, h, x, justify) = ('0', 0, 0, None)
                        props = dollar[7:]
                        if len(props) > 0:
                            if ',' in props:
                                if props[0] != ',':
                                    w = props[:props.index(',')]
                                h = int(props[props.index(',') + 1:])
                            else:
                                w = props
                        if 'l' in w:
                            (x, w) = (int(w[:w.find('l')]), int(w[w.find('l') + 1:]))
                            justify = 'l'
                            w -= x;
                        elif 'c' in w:
                            (x, w) = (int(w[:w.find('c')]), int(w[w.find('c') + 1:]))
                            justify = 'c'
                            w -= x;
                        elif 'r' in w:
                            (x, w) = (int(w[:w.find('r')]), int(w[w.find('r') + 1:]))
                            justify = 'r'
                            w -= x;
                        else:
                            w = int(w)
                        balloon = self.__getBalloon(w, h, x, justify, indent)
                        balloon = balloon.split('\n')
                        balloon = [AUTO_PUSH + self.ballooncolour + item + AUTO_POP for item in balloon]
                        for b in balloon[0]:
                            self.output += b + colourstack.feed(b)
                        if lineindex == 0:
                            balloonpre = '\n' + (' ' * indent)
                            for line in balloon[1:]:
                                self.output += balloonpre;
                                for b in line:
                                    self.output += b + colourstack.feed(b);
                            indent = 0
                        elif len(balloon) > 1:
                            balloonLines = balloon
                            balloonLine = 0
                            balloonIndent = indent
                            indent += Backend.len(balloonLines[0])
                            balloonLines[0] = None
                    dollar = None
                else:
                    dollar = ''
            elif dollar is not None:
                if c == '\033':
                    c = self.pony[i]
                    i += 1
                dollar += c
            elif c == '\033':
                colour = Backend.getColour(self.pony, i - 1)
                for b in colour:
                    self.output += b + colourstack.feed(b);
                i += len(colour) - 1
            elif c == '\n':
                self.output += c
                indent = 0
                (skip, nonskip) = (0, 0)
                lineindex += 1
                if balloonLines is not None:
                    balloonLine += 1
                    if balloonLine == len(balloonLines):
                        balloonLines = None
            else:
                if (balloonLines is not None) and (balloonLines[balloonLine] is not None) and (balloonIndent == indent):
                    data = balloonLines[balloonLine]
                    datalen = Backend.len(data)
                    skip += datalen
                    nonskip += datalen
                    data = data.replace('$', '$$')
                    n += len(data)
                    self.pony = self.pony[:i] + data + self.pony[i:]
                    balloonLines[balloonLine] = None
                else:
                    if (skip == 0) or (nonskip > 0):
                        if nonskip > 0:
                            nonskip -= 1
                        self.output += c + colourstack.feed(c);
                        if not UCS.isCombining(c):
                            indent += 1
                    else:
                        skip -= 1
        
        if balloonLines is not None:
            for line in balloonLines[balloonLine:]:
                data = ' ' * (balloonIndent - indent) + line + '\n'
                for b in data:
                    self.output += b + colourstack.feed(b);
                indent = 0
        
        self.output = self.output.replace(AUTO_PUSH, '').replace(AUTO_POP, '')
        
        if self.balloon is None:
            if (self.balloontop > 0) or (self.balloonbottom > 0):
                self.output = self.output.split('\n')
                self.output = self.output[self.balloontop : ~(self.balloonbottom)]
                self.output = '\n'.join(self.output)
    
    
    @staticmethod
    def getColour(input, offset):
        '''
        Gets colour code att the currect offset in a buffer
        
        @param   input:str   The input buffer
        @param   offset:int  The offset at where to start reading, a escape must begin here
        @return  :str        The escape sequence
        '''
        (i, n) = (offset, len(input))
        rc = input[i]
        i += 1
        if i == n: return rc
        c = input[i]
        i += 1
        rc += c
        
        if c == ']':
            if i == n: return rc
            c = input[i]
            i += 1
            rc += c
            if c == 'P':
                di = 0
                while (di < 7) and (i < n):
                    c = input[i]
                    i += 1
                    di += 1
                    rc += c
            while c == '0':
                c = input[i]
                i += 1
                rc += c
            if c == '4':
                c = input[i]
                i += 1
                rc += c
                if c == ';':
                    c = input[i]
                    i += 1
                    rc += c
                    while c != '\\':
                        c = input[i]
                        i += 1
                        rc += c
        elif c == '[':
            while i < n:
                c = input[i]
                i += 1
                rc += c
                if (c == '~') or (('a' <= c) and (c <= 'z')) or (('A' <= c) and (c <= 'Z')):
                    break
        
        return rc
    
    
    @staticmethod
    def len(input):
        '''
        Calculates the number of visible characters in a text
        
        @param   input:str  The input buffer
        @return  :int       The number of visible characters
        '''
        (rc, i, n) = (0, 0, len(input))
        while i < n:
            c = input[i]
            if c == '\033':
                i += len(Backend.getColour(input, i))
            else:
                i += 1
                if not UCS.isCombining(c):
                    rc += 1
                    if unicodedata.east_asian_width(c) in ('F', 'W'):
                        rc += 1
        return rc
    
    
    def __getBalloon(self, width, height, innerleft, justify, left):
        '''
        Generates a balloon with the message
        
        @param   width:int      The minimum width of the balloon
        @param   height:int     The minimum height of the balloon
        @param   innerleft:int  The left column of the required span, excluding that of `left`
        @param   justify:str    Balloon placement justification, 'c' → centered,
                                'l' → left (expand to right), 'r' → right (expand to left)
        @param   left:int       The column where the balloon starts
        @return  :str           The balloon the the message as a string
        '''
        wrap = None
        if self.wrapcolumn is not None:
            wrap = self.wrapcolumn - left
            if wrap < 8:
                wrap = 8
        
        msg = self.message
        if wrap is not None:
            msg = self.__wrapMessage(msg, wrap)
        
        msg = msg.replace('\n', '\033[0m%s\n' % (self.ballooncolour)) + '\033[0m' + self.ballooncolour
        msg = msg.split('\n')
        
        extraleft = 0
        if justify is not None:
            msgwidth = self.len(max(msg, key = self.len)) + self.balloon.minwidth
            extraleft = innerleft
            if msgwidth > width:
                if (justify == 'l') and (wrap is not None):
                    if innerleft + msgwidth > wrap:
                        extraleft -= msgwidth - wrap
                elif justify == 'r':
                    extraleft -= msgwidth - width
                elif justify == 'c':
                    extraleft -= (msgwidth - width) >> 1
                    if extraleft < 0:
                        extraleft = 0
                    if wrap is not None:
                        if extraleft + msgwidth > wrap:
                            extraleft -= msgwidth - wrap
        
        rc = self.balloon.get(width, height, msg, Backend.len);
        if extraleft > 0:
            rc = ' ' * extraleft + rc.replace('\n', '\n' + ' ' * extraleft)
        return rc
    
    
    def __wrapMessage(self, message, wrap):
        '''
        Wraps the message
        
        @param   message:str  The message to wrap
        @param   wrap:int     The width at where to force wrapping
        @return  :str         The message wrapped
        '''
        wraplimit = os.environ['PONYSAY_WRAP_LIMIT'] if 'PONYSAY_WRAP_LIMIT' in os.environ else ''
        wraplimit = 8 if len(wraplimit) == 0 else int(wraplimit)
        
        wrapexceed = os.environ['PONYSAY_WRAP_EXCEED'] if 'PONYSAY_WRAP_EXCEED' in os.environ else ''
        wrapexceed = 5 if len(wrapexceed) == 0 else int(wrapexceed)
        
        buf = ''
        try:
            AUTO_PUSH = '\033[01010~'
            AUTO_POP  = '\033[10101~'
            msg = message.replace('\n', AUTO_PUSH + '\n' + AUTO_POP)
            cstack = ColourStack(AUTO_PUSH, AUTO_POP)
            for c in msg:
                buf += c + cstack.feed(c)
            lines = buf.replace(AUTO_PUSH, '').replace(AUTO_POP, '').split('\n')
            buf = ''
            
            for line in lines:
                b = [None] * len(line)
                map = {0 : 0}
                (bi, cols, w) = (0, 0, wrap)
                (indent, indentc) = (-1, 0)
                
                (i, n) = (0, len(line))
                while i <= n:
                    d = None
                    if i < n:
                        d = line[i]
                    i += 1
                    if d == '\033':
                        ## Invisible stuff
                        i -= 1
                        colourseq = Backend.getColour(line, i)
                        b[bi : bi + len(colourseq)] = colourseq
                        i += len(colourseq)
                        bi += len(colourseq)
                    elif (d is not None) and (d != ' '):
                        ## Fetch word
                        if indent == -1:
                            indent = i - 1
                            for j in range(0, indent):
                                if line[j] == ' ':
                                    indentc += 1
                        b[bi] = d
                        bi += 1
                        if (not UCS.isCombining(d)) and (d != '­'):
                            cols += 1
                        map[cols] = bi
                    else:
                        ## Wrap?
                        mm = 0
                        bisub = 0
                        iwrap = wrap - (0 if indent == 1 else indentc)
                        
                        while ((w > wraplimit) and (cols > w + wrapexceed)) or (cols > iwrap):
                            ## wrap
                            x = w;
                            if mm + x not in map: # Too much whitespace?
                                cols = 0
                                break
                            nbsp = b[map[mm + x]] == ' ' # nbsp
                            m = map[mm + x]
                            
                            if ('­' in b[bisub : m]) and not nbsp: # soft hyphen
                                hyphen = m - 1
                                while b[hyphen] != '­': # soft hyphen
                                    hyphen -= 1
                                while map[mm + x] > hyphen: ## Only looking backward, if forward is required the word is probabily not hyphenated correctly
                                    x -= 1
                                x += 1
                                m = map[mm + x]
                            
                            mm += x - (0 if nbsp else 1) ## − 1 so we have space for a hythen
                            
                            for bb in b[bisub : m]:
                                buf += bb
                            buf += '\n' if nbsp else '\0\n'
                            cols -= x - (0 if nbsp else 1)
                            bisub = m
                            
                            w = iwrap
                            if indent != -1:
                                buf += ' ' * indentc
                        
                        for j in range(bisub, bi):
                            b[j - bisub] = b[j]
                        bi -= bisub
                        
                        if cols > w:
                            buf += '\n'
                            w = wrap
                            if indent != -1:
                                buf += ' ' * indentc
                                w -= indentc
                        for bb in b[:bi]:
                            if bb is not None:
                                buf += bb
                        w -= cols
                        cols = 0
                        bi = 0
                        if d is None:
                            i += 1
                        else:
                            if w > 0:
                                buf += ' '
                                w -= 1
                            else:
                                buf += '\n'
                                w = wrap
                                if indent != -1:
                                    buf += ' ' * indentc
                                    w -= indentc
                buf += '\n'
            
            rc = '\n'.join(line.rstrip(' ') for line in buf[:-1].split('\n'));
            rc = rc.replace('­', ''); # remove soft hyphens
            rc = rc.replace('\0', '%s%s%s' % (AUTO_PUSH, self.hyphen, AUTO_POP))
            return rc
        except Exception as err:
            import traceback
            errormessage = ''.join(traceback.format_exception(type(err), err, None))
            rc = '\n'.join(line.rstrip(' ') for line in buf.split('\n'));
            rc = rc.replace('\0', '%s%s%s' % (AUTO_PUSH, self.hyphen, AUTO_POP))
            errormessage += '\n---- WRAPPING BUFFER ----\n\n' + rc
            try:
                if os.readlink('/proc/self/fd/2') != os.readlink('/proc/self/fd/1'):
                    printerr(errormessage, end='')
                    return message
            except:
                pass
            return message + '\n\n\033[0;1;31m---- EXCEPTION IN PONYSAY WHILE WRAPPING ----\033[0m\n\n' + errormessage

