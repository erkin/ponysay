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

import os
import sys
from subprocess import Popen, PIPE

from argparser import *
from ponysay import *
from metadata import *


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



class PonysayTool():
    '''
    This is the mane class of ponysay-tool
    '''
    
    def __init__(self, args):
        '''
        Starts the part of the program the arguments indicate
        
        @param  args:ArgParser  Parsed command line arguments
        '''
        if args.argcount == 0:
            args.help()
            exit(255)
            return
        
        opts = args.opts
        
        if unrecognised or (opts['-h'] is not None) or (opts['+h'] is not None):
            args.help(True if opts['+h'] is not None else None)
            if unrecognised:
                exit(254)
        
        elif opts['-v'] is not None:
            print('%s %s' % ('ponysay-tool', VERSION))
        
        elif opts['--kms'] is not None:
            self.generateKMS()
        
        elif (opts['--dimensions'] is not None) and (len(opts['--dimensions']) == 1):
            self.generateDimensions(opts['--dimensions'][0], args.files)
        
        elif (opts['--metadata'] is not None) and (len(opts['--metadata']) == 1):
            self.generateMetadata(opts['--metadata'][0], args.files)
        
        elif (opts['-b'] is not None) and (len(opts['-b']) == 1):
            try:
                if opts['--no-term-init'] is None:
                    print('\033[?1049h', end='') # initialise terminal
                cmd = 'stty %s < %s > /dev/null 2> /dev/null'
                cmd %= ('-echo -icanon -echo -isig -ixoff -ixon', os.path.realpath('/dev/stdout'))
                Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE).wait()
                print('\033[?25l', end='') # hide cursor
                dir = opts['-b'][0]
                if not dir.endswith(os.sep):
                    dir += os.sep
                self.browse(dir, opts['-r'])
            finally:
                print('\033[?25h', end='') # show cursor
                cmd = 'stty %s < %s > /dev/null 2> /dev/null'
                cmd %= ('echo icanon echo isig ixoff ixon', os.path.realpath('/dev/stdout'))
                Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE).wait()
                if opts['--no-term-init'] is None:
                    print('\033[?1049l', end='') # terminate terminal
        
        elif (opts['--edit'] is not None) and (len(opts['--edit']) == 1):
            pony = opts['--edit'][0]
            if not os.path.isfile(pony):
                printerr('%s is not an existing regular file' % pony)
                exit(252)
            linuxvt = ('TERM' in os.environ) and (os.environ['TERM'] == 'linux')
            try:
                if opts['--no-term-init'] is None:
                    print('\033[?1049h', end='') # initialise terminal
                if linuxvt: print('\033[?8c', end='') # use full block for cursor (_ is used by default in linux vt)
                cmd = 'stty %s < %s > /dev/null 2> /dev/null'
                cmd %= ('-echo -icanon -echo -isig -ixoff -ixon', os.path.realpath('/dev/stdout'))
                Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE).wait()
                self.editmeta(pony)
            finally:
                cmd = 'stty %s < %s > /dev/null 2> /dev/null'
                cmd %= ('echo icanon echo isig ixoff ixon', os.path.realpath('/dev/stdout'))
                Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE).wait()
                if linuxvt: print('\033[?0c', end='') # restore cursor
                if opts['--no-term-init'] is None:
                    print('\033[?1049l', end='') # terminate terminal
        
        elif (opts['--edit-rm'] is not None) and (len(opts['--edit-rm']) == 1):
            ponyfile = opts['--edit-rm'][0]
            pony = None
            with open(ponyfile, 'rb') as file:
                pony = file.read().decode('utf8', 'replace')
            if pony.startswith('$$$\n'):
                pony = pony[3:]
                pony = pony[pony.index('\n$$$\n') + 5:]
                with open(ponyfile, 'wb') as file:
                    file.write(pony.encode('utf8'))
        
        elif (opts['--edit-stash'] is not None) and (len(opts['--edit-stash']) == 1):
            ponyfile = opts['--edit-stash'][0]
            pony = None
            with open(ponyfile, 'rb') as file:
                pony = file.read().decode('utf8', 'replace')
            if pony.startswith('$$$\n'):
                pony = pony[3:]
                pony = pony[:pony.index('\n$$$\n')]
                print('$$$' + pony + '\n$$$\n', end='')
            else:
                print('$$$\n$$$\n', end='')
        
        elif (opts['--edit-apply'] is not None) and (len(opts['--edit-apply']) == 1):
            data = ''
            while True:
                line = input()
                if data == '':
                    if line != '$$$':
                        printerr('Bad stash')
                        exit(251)
                    data += '$$$\n'
                else:
                    data += line + '\n'
                    if line == '$$$':
                        break
            ponyfile = opts['--edit-apply'][0]
            pony = None
            with open(ponyfile, 'rb') as file:
                pony = file.read().decode('utf8', 'replace')
            if pony.startswith('$$$\n'):
                pony = pony[3:]
                pony = pony[pony.index('\n$$$\n') + 5:]
            with open(ponyfile, 'wb') as file:
                file.write((data + pony).encode('utf8'))
        
        else:
            args.help()
            exit(253)
    
    
    def execPonysay(self, args, message = ''):
        '''
        Execute ponysay!
        
        @param  args     Arguments
        @param  message  Message
        '''
        class PhonyArgParser():
            def __init__(self, args, message):
                self.argcount = len(args) + (0 if message is None else 1)
                for key in args:
                    self.argcount += len(args[key]) if (args[key] is not None) and isinstance(args[key], list) else 1
                self.message = message
                self.opts = self
            def __getitem__(self, key):
                if key in args:
                    return args[key] if (args[key] is not None) and isinstance(args[key], list) else [args[key]]
                return None
            def __contains__(self, key):
                return key in args;
        
        stdout = sys.stdout
        class StringInputStream():
            def __init__(self):
                self.buf = ''
                class Buffer():
                    def __init__(self, parent):
                        self.parent = parent
                    def write(self, data):
                        self.parent.buf += data.decode('utf8', 'replace')
                    def flush(self):
                        pass
                self.buffer = Buffer(self)
            def flush(self):
                pass
            def isatty(self):
                return True
        sys.stdout = StringInputStream()
        ponysay = Ponysay()
        ponysay.run(PhonyArgParser(args, message))
        out = sys.stdout.buf[:-1]
        sys.stdout = stdout
        return out
    
    
    def browse(self, ponydir, restriction):
        '''
        Browse ponies
        
        @param  ponydir:str            The pony directory to browse
        @param  restriction:list<str>  Restrictions on listed ponies, may be None
        '''
        ## Call `stty` to determine the size of the terminal, this way is better than using python's ncurses
        termsize = None
        for channel in (sys.stdout, sys.stdin, sys.stderr):
            termsize = Popen(['stty', 'size'], stdout=PIPE, stdin=channel, stderr=PIPE).communicate()[0]
            if len(termsize) > 0:
                termsize = termsize.decode('utf8', 'replace')[:-1].split(' ') # [:-1] removes a \n
                termsize = [int(item) for item in termsize]
                break
        (termh, termw) = termsize
        
        ponies = set()
        for ponyfile in os.listdir(ponydir):
            if endswith(ponyfile, '.pony'):
                ponyfile = ponyfile[:-5]
                if ponyfile not in ponies:
                    ponies.add(ponyfile)
        if restriction is not None:
            oldponies = ponies
            logic = Metadata.makeRestrictionLogic(restriction)
            ponies = set()
            for pony in Metadata.restrictedPonies(ponydir, logic):
                if (pony not in ponies) and (pony in oldponies):
                    ponies.add(pony)
            oldponies = ponies
        ponies = list(ponies)
        ponies.sort()
        
        if len(ponies) == 0:
            print('\033[1;31m%s\033[21m;39m' % 'No ponies... press Enter to exit.')
            input()
        
        panelw = Backend.len(max(ponies, key = Backend.len))
        panely = 0
        panelx = termw - panelw
        
        (x, y) = (0, 0)
        (oldx, oldy) = (None, None)
        (quotes, info) = (False, False)
        (ponyindex, oldpony) = (0, None)
        (pony, ponywidth, ponyheight) = (None, None, None)
        
        stored = None
        while True:
            printpanel = -2 if ponyindex != oldpony else oldpony
            if (ponyindex != oldpony):
                ponyindex %= len(ponies)
                if ponyindex < 0:
                    ponyindex += len(ponies)
                oldpony = ponyindex
                
                ponyfile = (ponydir + '/' + ponies[ponyindex] + '.pony').replace('//', '/')
                pony = self.execPonysay({'-f' : ponyfile, '-W' : 'none', '-o' : None}).split('\n')
                
                preprint = '\033[H\033[2J'
                if pony[0].startswith(preprint):
                    pony[0] = pony[0][len(preprint):]
                ponyheight = len(pony)
                ponywidth = Backend.len(max(pony, key = Backend.len))
                
                AUTO_PUSH = '\033[01010~'
                AUTO_POP  = '\033[10101~'
                pony = '\n'.join(pony).replace('\n', AUTO_PUSH + '\n' + AUTO_POP)
                colourstack = ColourStack(AUTO_PUSH, AUTO_POP)
                buf = ''
                for c in pony:
                    buf += c + colourstack.feed(c)
                pony = buf.replace(AUTO_PUSH, '').replace(AUTO_POP, '').split('\n')
            
            if (oldx != x) or (oldy != y):
                (oldx, oldy) = (x, y)
                print('\033[H\033[2J', end='')
                
                def getprint(pony, ponywidth, ponyheight, termw, termh, px, py):
                    ponyprint = pony
                    if py < 0:
                        ponyprint = [] if -py > len(ponyprint) else ponyprint[-py:]
                    elif py > 0:
                        ponyprint = py * [''] + ponyprint
                    ponyprint = ponyprint[:len(ponyprint) if len(ponyprint) < termh else termh]
                    def findcolumn(line, column):
                        if Backend.len(line) >= column:
                            return len(line)
                        pos = len(line)
                        while Backend.len(line[:pos]) != column:
                            pos -= 1
                        return pos
                    if px < 0:
                        ponyprint = [('' if -px > Backend.len(line) else line[findcolumn(line, -px):]) for line in ponyprint]
                    elif px > 0:
                        ponyprint = [px * ' ' + line for line in ponyprint]
                    ponyprint = [(line if Backend.len(line) <= termw else line[:findcolumn(line, termw)]) for line in ponyprint]
                    ponyprint = ['\033[21;39;49;0m%s\033[21;39;49;0m' % line for line in ponyprint]
                    return '\n'.join(ponyprint)
                
                if quotes:
                    ponyquotes = None # TODO
                    quotesheight = len(ponyquotes)
                    quoteswidth = Backend.len(max(ponyquotes, key = Backend.len))
                    print(getprint(ponyquotes, quoteswidth, quotesheight, termw, termh, x, y), end='')
                elif info:
                    ponyfile = (ponydir + '/' + ponies[ponyindex] + '.pony').replace('//', '/')
                    ponyinfo = self.execPonysay({'-f' : ponyfile, '-W' : 'none', '-i' : None}).split('\n')
                    infoheight = len(ponyinfo)
                    infowidth = Backend.len(max(ponyinfo, key = Backend.len))
                    print(getprint(ponyinfo, infowidth, infoheight, termw, termh, x, y), end='')
                else:
                    print(getprint(pony, ponywidth, ponyheight, panelx, termh, x + (panelx - ponywidth) // 2, y + (termh - ponyheight) // 2), end='')
                    printpanel = -1
            
            if printpanel == -1:
                cury = 0
                for line in ponies[panely:]:
                    cury += 1
                    if os.path.islink((ponydir + '/' + line + '.pony').replace('//', '/')):
                        line = '\033[34m%s\033[39m' % ((line + ' ' * panelw)[:panelw])
                    else:
                        line = (line + ' ' * panelw)[:panelw]
                    print('\033[%i;%iH\033[%im%s\033[0m' % (cury, panelx + 1, 1 if panely + cury - 1 == ponyindex else 0, line), end='')
            elif printpanel >= 0:
                for index in (printpanel, ponyindex):
                    cury = index - panely
                    if (0 <= cury) and (cury < termh):
                        line = ponies[cury + panely]
                        if os.path.islink((ponydir + '/' + line + '.pony').replace('//', '/')):
                            line = '\033[34m%s\033[39m' % ((line + ' ' * panelw)[:panelw])
                        else:
                            line = (line + ' ' * panelw)[:panelw]
                        print('\033[%i;%iH\033[%im%s\033[0m' % (cury, panelx + 1, 1 if panely + cury - 1 == ponyindex else 0, line), end='')
            
            sys.stdout.buffer.flush()
            if stored is None:
                d = sys.stdin.read(1)
            else:
                d = stored
                stored = None
            
            recenter = False
            if (d == 'w') or (d == 'W') or (d == '<') or (d == 'ä') or (d == 'Ä'): # pad ↑
                y -= 1
            elif (d == 's') or (d == 'S') or (d == 'o') or (d == 'O'): # pad ↓
                y += 1
            elif (d == 'd') or (d == 'D') or (d == 'e') or (d == 'E'): # pad →
                x += 1
            elif (d == 'a') or (d == 'A'): # pad ←
                x -= 1
            elif (d == 'q') or (d == 'Q'): # toggle quotes
                quotes = False if info else not quotes
                recenter = True
            elif (d == 'i') or (d == 'I'): # toggle metadata
                info = False if quotes else not info
                recenter = True
            elif ord(d) == ord('L') - ord('@'): # recenter
                recenter = True
            elif ord(d) == ord('P') - ord('@'): # previous
                ponyindex -= 1
                recenter = True
            elif ord(d) == ord('N') - ord('@'): # next
                ponyindex += 1
                recenter = True
            elif ord(d) == ord('Q') - ord('@'):
                break
            elif ord(d) == ord('X') - ord('@'):
                if ord(sys.stdin.read(1)) == ord('C') - ord('@'):
                    break
            elif d == '\033':
                d = sys.stdin.read(1)
                if d == '[':
                    d = sys.stdin.read(1)
                    if   d == 'A':  stored = chr(ord('P') - ord('@')) if (not quotes) and (not info) else 'W'
                    elif d == 'B':  stored = chr(ord('N') - ord('@')) if (not quotes) and (not info) else 'S'
                    elif d == 'C':  stored = chr(ord('N') - ord('@')) if (not quotes) and (not info) else 'D'
                    elif d == 'D':  stored = chr(ord('P') - ord('@')) if (not quotes) and (not info) else 'A'
                    elif d == '1':
                        if sys.stdin.read(1) == ';':
                            if sys.stdin.read(1) == '5':
                                d = sys.stdin.read(1)
                                if   d == 'A':  stored = 'W'
                                elif d == 'B':  stored = 'S'
                                elif d == 'C':  stored = 'D'
                                elif d == 'D':  stored = 'A'
            if recenter:
                (oldx, oldy) = (None, None)
                (x, y) = (0, 0)
    
    
    def generateKMS(self):
        '''
        Generate all kmsponies for the current TTY palette
        '''
        class PhonyArgParser():
            def __init__(self, key, value):
                self.argcount = 3
                self.message = ''
                self.opts = self
                self.key = key
                self.value = value
            def __getitem__(self, key):
                return [self.value] if key == self.key else None
            def __contains__(self, key):
                return key == self.key;
        
        class StringInputStream():
            def __init__(self):
                self.buf = ''
                class Buffer():
                    def __init__(self, parent):
                        self.parent = parent
                    def write(self, data):
                        self.parent.buf += data.decode('utf8', 'replace')
                    def flush(self):
                        pass
                self.buffer = Buffer(self)
            def flush(self):
                pass
            def isatty(self):
                return True
        
        stdout = sys.stdout
        term = os.environ['TERM']
        os.environ['TERM'] = 'linux'
        
        sys.stdout = StringInputStream()
        ponysay = Ponysay()
        ponysay.run(PhonyArgParser('--onelist', None))
        stdponies = sys.stdout.buf[:-1].split('\n')
        
        sys.stdout = StringInputStream()
        ponysay = Ponysay()
        ponysay.run(PhonyArgParser('++onelist', None))
        extraponies = sys.stdout.buf[:-1].split('\n')
        
        for pony in stdponies:
            printerr('Genering standard kmspony: %s' % pony)
            sys.stderr.buffer.flush();
            sys.stdout = StringInputStream()
            ponysay = Ponysay()
            ponysay.run(PhonyArgParser('--pony', pony))
        
        for pony in extraponies:
            printerr('Genering extra kmspony: %s' % pony)
            sys.stderr.buffer.flush();
            sys.stdout = StringInputStream()
            ponysay = Ponysay()
            ponysay.run(PhonyArgParser('++pony', pony))
        
        os.environ['TERM'] = term
        sys.stdout = stdout
    
    
    def generateDimensions(self, ponydir, ponies = None):
        '''
        Generate pony dimension file for a directory
        
        @param  ponydir:str        The directory
        @param  ponies:itr<str>?   Ponies to which to limit
        '''
        dimensions = []
        ponyset = None if (ponies is None) or (len(ponies) == 0) else set(ponies)
        for ponyfile in os.listdir(ponydir):
            if (ponyset is not None) and (ponyfile not in ponyset):
                continue
            if ponyfile.endswith('.pony') and (ponyfile != '.pony'):
                class PhonyArgParser():
                    def __init__(self, balloon):
                        self.argcount = 5
                        self.message = ''
                        self.pony = (ponydir + '/' + ponyfile).replace('//', '/')
                        self.balloon = balloon
                        self.opts = self
                    def __getitem__(self, key):
                        if key == '-f':
                            return [self.pony]
                        if key == ('-W' if self.balloon else '-b'):
                            return [('none' if self.balloon else None)]
                        return None
                    def __contains__(self, key):
                        return key in ('-f', '-W', '-b');
                stdout = sys.stdout
                class StringInputStream():
                    def __init__(self):
                        self.buf = ''
                        class Buffer():
                            def __init__(self, parent):
                                self.parent = parent
                            def write(self, data):
                                self.parent.buf += data.decode('utf8', 'replace')
                            def flush(self):
                                pass
                        self.buffer = Buffer(self)
                    def flush(self):
                        pass
                    def isatty(self):
                        return True
                sys.stdout = StringInputStream()
                ponysay = Ponysay()
                ponysay.run(PhonyArgParser(True))
                printpony = sys.stdout.buf[:-1].split('\n')
                ponyheight = len(printpony) - 2 # using fallback balloon
                ponywidth = Backend.len(max(printpony, key = Backend.len))
                ponysay = Ponysay()
                ponysay.run(PhonyArgParser(False))
                printpony = sys.stdout.buf[:-1].split('\n')
                ponyonlyheight = len(printpony)
                sys.stdout = stdout
                dimensions.append((ponywidth, ponyheight, ponyonlyheight, ponyfile[:-5]))
        (widths, heights, onlyheights) = ([], [], [])
        for item in dimensions:
            widths     .append((item[0], item[3]))
            heights    .append((item[1], item[3]))
            onlyheights.append((item[2], item[3]))
        for items in (widths, heights, onlyheights):
            sorted(items, key = lambda item : item[0])
        for pair in ((widths, 'widths'), (heights, 'heights'), (onlyheights, 'onlyheights')):
            (items, dimfile) = pair
            dimfile = (ponydir + '/' + dimfile).replace('//', '/')
            ponies = [item[1] for item in items]
            dims = []
            last = -1
            index = 0
            for item in items:
                cur = item[0]
                if cur != last:
                    if last >= 0:
                        dims.append((last, index))
                    last = cur
                index += 1
            if last >= 0:
                dims.append((last, index))
            dims = ''.join([('%i/%i/' % (dim[0], len('/'.join(ponies[:dim[1]])))) for dim in dims])
            data = '/' + str(len(dims)) + '/' + dims + '/'.join(ponies) + '/'
            with open(dimfile, 'wb') as file:
                file.write(data.encode('utf8'))
                file.flush()
    
    
    def generateMetadata(self, ponydir, ponies = None):
        '''
        Generate pony metadata collection file for a directory
        
        @param  ponydir:str       The directory
        @param  ponies:itr<str>?  Ponies to which to limit
        '''
        if not ponydir.endswith('/'):
            ponydir += '/'
        def makeset(value):
            rc = set()
            bracket = 0
            esc = False
            buf = ''
            for c in value:
                if esc:
                    if bracket == 0:
                        if c not in (',', '\\', '(', ')'):
                            buf += '\\'
                        buf += c
                    esc = False
                elif c == '(':
                    bracket += 1
                elif c == ')':
                    if bracket == 0:
                        raise Exception('Bracket mismatch')
                    bracket -= 1
                elif c == '\\':
                    esc = True
                elif bracket == 0:
                    if c == ',':
                        buf = buf.strip()
                        if len(buf) > 0:
                            rc.add(buf)
                        buf = ''
                    else:
                        buf += c
            if bracket > 0:
                raise Exception('Bracket mismatch')
            buf = buf.strip()
            if len(buf) > 0:
                rc.add(buf)
            return rc
        everything = []
        ponyset = None if (ponies is None) or (len(ponies) == 0) else set(ponies)
        for ponyfile in os.listdir(ponydir):
            if (ponyset is not None) and (ponyfile not in ponyset):
                continue
            if ponyfile.endswith('.pony') and (ponyfile != '.pony'):
                with open(ponydir + ponyfile, 'rb') as file:
                    data = file.read().decode('utf8', 'replace')
                    data = [line.replace('\n', '') for line in data.split('\n')]
                if data[0] != '$$$':
                    meta = []
                else:
                    sep = 1
                    while data[sep] != '$$$':
                        sep += 1
                    meta = data[1 : sep]
                data = {}
                for line in meta:
                    if ':' in line:
                        key = line[:line.find(':')].strip()
                        value = line[line.find(':') + 1:]
                        test = key
                        for c in 'ABCDEFGHIJKLMN OPQRSTUVWXYZ':
                            test = test.replace(c, '')
                        if (len(test) == 0) and (len(key) > 0):
                            vals = makeset(value.replace(' ', ''))
                            if key not in data:
                                data[key] = vals
                            else:
                                dset = data[key]
                                for val in vals:
                                    dset.add(val)
                everything.append((ponyfile[:-5], data))
        import pickle
        with open((ponydir + '/metadata').replace('//', '/'), 'wb') as file:
            pickle.dump(everything, file, -1)
            file.flush()
    
    
    def editmeta(self, ponyfile):
        '''
        Edit a pony file's metadata
        
        @param  ponyfile:str  A pony file to edit
        '''
        (data, meta, image) = 3 * [None]
        
        with open(ponyfile, 'rb') as file:
            data = file.read().decode('utf8', 'replace')
            data = [line.replace('\n', '') for line in data.split('\n')]
        
        if data[0] != '$$$':
            image = data
            meta = []
        else:
            sep = 1
            while data[sep] != '$$$':
                sep += 1
            meta = data[1 : sep]
            image = data[sep + 1:]
        
        
        class PhonyArgParser():
            def __init__(self):
                self.argcount = 5
                self.message = ponyfile
                self.opts = self
            def __getitem__(self, key):
                if key == '-f':  return [ponyfile]
                if key == '-W':  return ['n']
                return None
            def __contains__(self, key):
                return key in ('-f', '-W');
        
        
        data = {}
        comment = []
        for line in meta:
            if ': ' in line.replace('\t', ' '):
                key = line.replace('\t', ' ')
                key = key[:key.find(': ')]
                test = key
                for c in 'ABCDEFGHIJKLMN OPQRSTUVWXYZ':
                    test = test.replace(c, '')
                if (len(test) == 0) and (len(key.replace(' ', '')) > 0):
                    key = key.strip(' ')
                    value = line.replace('\t', ' ')
                    value = value[value.find(': ') + 2:]
                    if key not in data:
                        data[key] = value.strip(' ')
                    else:
                        data[key] += '\n' + value.strip(' ')
                else:
                    comment.append(line)
            else:
                comment.append(line)
        
        cut = 0
        while (len(comment) > cut) and (len(comment[cut]) == 0):
            cut += 1
        comment = comment[cut:]
        
        
        stdout = sys.stdout
        class StringInputStream():
            def __init__(self):
                self.buf = ''
                class Buffer():
                    def __init__(self, parent):
                        self.parent = parent
                    def write(self, data):
                        self.parent.buf += data.decode('utf8', 'replace')
                    def flush(self):
                        pass
                self.buffer = Buffer(self)
            def flush(self):
                pass
            def isatty(self):
                return True
        sys.stdout = StringInputStream()
        ponysay = Ponysay()
        ponysay.run(PhonyArgParser())
        printpony = sys.stdout.buf[:-1].split('\n')
        sys.stdout = stdout
        
        preprint = '\033[H\033[2J'
        if printpony[0].startswith(preprint):
            printpony[0] = printpony[0][len(preprint):]
        ponyheight = len(printpony) - len(ponyfile.split('\n')) + 1 - 2 # using fallback balloon
        ponywidth = Backend.len(max(printpony, key = Backend.len))
        
        ## Call `stty` to determine the size of the terminal, this way is better than using python's ncurses
        termsize = None
        for channel in (sys.stdout, sys.stdin, sys.stderr):
            termsize = Popen(['stty', 'size'], stdout=PIPE, stdin=channel, stderr=PIPE).communicate()[0]
            if len(termsize) > 0:
                termsize = termsize.decode('utf8', 'replace')[:-1].split(' ') # [:-1] removes a \n
                termsize = [int(item) for item in termsize]
                break
        
        AUTO_PUSH = '\033[01010~'
        AUTO_POP  = '\033[10101~'
        modprintpony = '\n'.join(printpony).replace('\n', AUTO_PUSH + '\n' + AUTO_POP)
        colourstack = ColourStack(AUTO_PUSH, AUTO_POP)
        buf = ''
        for c in modprintpony:
            buf += c + colourstack.feed(c)
        modprintpony = buf.replace(AUTO_PUSH, '').replace(AUTO_POP, '')
        
        printpony = [('\033[21;39;49;0m%s%s\033[21;39;49;0m' % (' ' * (termsize[1] - ponywidth), line)) for line in modprintpony.split('\n')]
        
        
        print(preprint, end='')
        print('\n'.join(printpony), end='')
        print('\033[H', end='')
        print('Please see the info manual for details on how to fill out this form')
        print()
        
        
        if 'WIDTH'  in data:  del data['WIDTH']
        if 'HEIGHT' in data:  del data['HEIGHT']
        data['comment'] = '\n'.join(comment)
        fields = [key for key in data]
        fields.sort()
	# List of info fields.
        standardfields = ['GROUP NAME', 'NAME', 'OTHER NAMES', 'APPEARANCE', 'KIND',
                          'GROUP', 'BALLOON', 'LINK', 'LINK ON', 'COAT', 'MANE', 'EYE',
                          'AURA', 'DISPLAY', 'BALLOON TOP', 'BALLOON BOTTOM', 'MASTER',
                          'POSE', 'BASED ON', 'SOURCE', 'MEDIA', 'LICENSE', 'FREE',
                          'comment']
        for standard in standardfields:
            if standard in fields:
                del fields[fields.index(standard)]
            if standard not in data:
                data[standard] = ''
        
        fields = standardfields[:-1] + fields + [standardfields[-1]]
        
        def saver(ponyfile, ponyheight, ponywidth, data, image):
            class Saver():
                def __init__(self, ponyfile, ponyheight, ponywidth, data, image):
                    (self.ponyfile, self.ponyheight, self.ponywidth, self.data, self.image) = (ponyfile, ponyheight, ponywidth, data, image)
                def __call__(self): # functor
                    comment = self.data['comment']
                    comment = ('\n' + comment + '\n').replace('\n$$$\n', '\n\\$$$\n')[:-1]
                    
                    meta = []
                    keys = [key for key in data]
                    keys.sort()
                    for key in keys:
                        if self.data[key] is None:
                            continue
                        if (key == 'comment') or (len(self.data[key].strip()) == 0):
                            continue
                        values = self.data[key].strip()
                        for value in values.split('\n'):
                            meta.append(key + ': ' + value)
                    
                    meta.append('WIDTH: ' + str(self.ponywidth))
                    meta.append('HEIGHT: ' + str(self.ponyheight))
                    # TODO auto fill in BALLOON {TOP,BOTTOM}
                    meta.append(comment)
                    meta = '\n'.join(meta)
                    ponydata = '$$$\n' + meta + '\n$$$\n' + '\n'.join(self.image)
                    
                    with open(self.ponyfile, 'wb') as file:
                        file.write(ponydata.encode('utf8'))
                        file.flush()
            return Saver(ponyfile, ponyheight, ponywidth, data, image)
        
        textarea = TextArea(fields, data, 1, 3, termsize[1] - ponywidth, termsize[0] - 2, termsize)
        textarea.run(saver(ponyfile, ponyheight, ponywidth, data, image))



class TextArea(): # TODO support small screens  (This is being work on in GNU-Pony/featherweight)
    '''
    GNU Emacs alike text area
    '''
    def __init__(self, fields, datamap, left, top, width, height, termsize):
        '''
        Constructor
        
        @param  fields:list<str>       Field names
        @param  datamap:dist<str,str>  Data map
        @param  left:int               Left position of the component
        @param  top:int                Top position of the component
        @param  width:int              Width of the component
        @param  height:int             Height of the component
        @param  termsize:(int,int)     The height and width of the terminal
        '''
        (self.fields, self.datamap, self.left, self.top, self.width, self.height, self.termsize) \
        = (fields, datamap, left, top, width - 1, height, termsize)
    
    
    def run(self, saver):
        '''
        Execute text reading
        
        @param  saver  Save method
        '''
        innerleft = UCS.dispLen(max(self.fields, key = UCS.dispLen)) + self.left + 3
        
        leftlines = []
        datalines = []
        
        for key in self.fields:
            for line in self.datamap[key].split('\n'):
                leftlines.append(key)
                datalines.append(line)
        
        (termh, termw) = self.termsize
        (y, x) = (0, 0)
        mark = None
        
        KILL_MAX = 50
        killring = []
        killptr = None
        
        def status(text):
            print('\033[%i;%iH\033[7m%s\033[27m\033[%i;%iH' % (termh - 1, 1, ' (' + text + ') ' + '-' * (termw - len(' (' + text + ') ')), self.top + y, innerleft + x), end='')
        
        status('unmodified')
        
        print('\033[%i;%iH' % (self.top, innerleft), end='')
        
        def alert(text):
            if text is None:
                alert('')
            else:
                print('\033[%i;%iH\033[2K%s\033[%i;%iH' % (termh, 1, text, self.top + y, innerleft + x), end='')
        
        modified = False
        override = False
        
        (oldy, oldx, oldmark) = (y, x, mark)
        stored = chr(ord('L') - ord('@'))
        alerted = False
        edited = False
        print('\033[%i;%iH' % (self.top + y, innerleft + x), end='')
        while True:
            if (oldmark is not None) and (oldmark >= 0):
                if oldmark < oldx:
                    print('\033[%i;%iH\033[49m%s\033[%i;%iH' % (self.top + oldy, innerleft + oldmark, datalines[oldy][oldmark : oldx], self.top + y, innerleft + x), end='')
                elif oldmark > oldx:
                    print('\033[%i;%iH\033[49m%s\033[%i;%iH' % (self.top + oldy, innerleft + oldx, datalines[oldy][oldx : oldmark], self.top + y, innerleft + x), end='')
            if (mark is not None) and (mark >= 0):
                if mark < x:
                    print('\033[%i;%iH\033[44;37m%s\033[49;39m\033[%i;%iH' % (self.top + y, innerleft + mark, datalines[y][mark : x], self.top + y, innerleft + x), end='')
                elif mark > x:
                    print('\033[%i;%iH\033[44;37m%s\033[49;39m\033[%i;%iH' % (self.top + y, innerleft + x, datalines[y][x : mark], self.top + y, innerleft + x), end='')
            if y != oldy:
                if (oldy > 0) and (leftlines[oldy - 1] == leftlines[oldy]) and (leftlines[oldy] == leftlines[-1]):
                    print('\033[%i;%iH\033[34m%s\033[39m' % (self.top + oldy, self.left, '>'), end='')
                else:
                    print('\033[%i;%iH\033[34m%s:\033[39m' % (self.top + oldy, self.left, leftlines[oldy]), end='')
                if (y > 0) and (leftlines[y - 1] == leftlines[y]) and (leftlines[y] == leftlines[-1]):
                    print('\033[%i;%iH\033[1;34m%s\033[21;39m' % (self.top + y, self.left, '>'), end='')
                else:
                    print('\033[%i;%iH\033[1;34m%s:\033[21;39m' % (self.top + y, self.left, leftlines[y]), end='')
                print('\033[%i;%iH' % (self.top + y, innerleft + x), end='')
            (oldy, oldx, oldmark) = (y, x, mark)
            if edited:
                edited = False
                if not modified:
                    modified = True
                    status('modified' + (' override' if override else ''))
            sys.stdout.flush()
            if stored is None:
                d = sys.stdin.read(1)
            else:
                d = stored
                stored = None
            if alerted:
                alerted = False
                alert(None)
            if ord(d) == ord('@') - ord('@'):
                if mark is None:
                    mark = x
                    alert('Mark set')
                elif mark == ~x:
                    mark = x
                    alert('Mark activated')
                elif mark == x:
                    mark = ~x
                    alert('Mark deactivated')
                else:
                    mark = x
                    alert('Mark set')
                alerted = True
            elif ord(d) == ord('K') - ord('@'):
                if x == len(datalines[y]):
                    alert('At end')
                    alerted = True
                else:
                    mark = len(datalines[y])
                    stored = chr(ord('W') - ord('@'))
            elif ord(d) == ord('W') - ord('@'):
                if (mark is not None) and (mark >= 0) and (mark != x):
                    selected = datalines[y][mark : x] if mark < x else datalines[y][x : mark]
                    killring.append(selected)
                    if len(killring) > KILL_MAX:
                        killring = killring[1:]
                    stored = chr(127)
                else:
                    alert('No text is selected')
                    alerted = True
            elif ord(d) == ord('Y') - ord('@'):
                if len(killring) == 0:
                    alert('Killring is empty')
                    alerted = True
                else:
                    mark = None
                    killptr = len(killring) - 1
                    yanked = killring[killptr]
                    print('\033[%i;%iH%s' % (self.top + y, innerleft + x, yanked + datalines[y][x:]), end='')
                    datalines[y] = datalines[y][:x] + yanked + datalines[y][x:]
                    x += len(yanked)
                    print('\033[%i;%iH' % (self.top + y, innerleft + x), end='')
            elif ord(d) == ord('X') - ord('@'):
                alert('C-x')
                alerted = True
                sys.stdout.flush()
                d = sys.stdin.read(1)
                alert(str(ord(d)))
                sys.stdout.flush()
                if ord(d) == ord('X') - ord('@'):
                    if (mark is not None) and (mark >= 0):
                        x ^= mark; mark ^= x; x ^= mark
                        alert('Mark swapped')
                    else:
                        alert('No mark is activated')
                elif ord(d) == ord('S') - ord('@'):
                    last = ''
                    for row in range(0, len(datalines)):
                        current = leftlines[row]
                        if len(datalines[row].strip()) == 0:
                            if current != 'comment':
                                if current != last:
                                    self.datamap[current] = None
                                continue
                        if current == last:
                            self.datamap[current] += '\n' + datalines[row]
                        else:
                            self.datamap[current] = datalines[row]
                            last = current
                    saver()
                    status('unmodified' + (' override' if override else ''))
                    alert('Saved')
                elif ord(d) == ord('C') - ord('@'):
                    break
                else:
                    stored = d
                    alerted = False
                    alert(None)
            elif (ord(d) == 127) or (ord(d) == 8):
                removed = 1
                if (mark is not None) and (mark >= 0) and (mark != x):
                    if mark > x:
                        x ^= mark; mark ^= x; x ^= mark
                    removed = x - mark
                if x == 0:
                    alert('At beginning')
                    alerted = True
                    continue
                dataline = datalines[y]
                datalines[y] = dataline = dataline[:x - removed] + dataline[x:]
                x -= removed
                mark = None
                print('\033[%i;%iH%s%s\033[%i;%iH' % (self.top + y, innerleft, dataline, ' ' * removed, self.top + y, innerleft + x), end='')
                edited = True
            elif ord(d) < ord(' '):
                if ord(d) == ord('P') - ord('@'):
                    if y == 0:
                        alert('At first line')
                        alerted = True
                    else:
                        y -= 1
                        mark = None
                        x = 0
                elif ord(d) == ord('N') - ord('@'):
                    if y == len(datalines) - 1:
                        datalines.append('')
                        leftlines.append(leftlines[-1])
                    y += 1
                    mark = None
                    x = 0
                elif ord(d) == ord('F') - ord('@'):
                    if x < len(datalines[y]):
                        x += 1
                        print('\033[C', end='')
                    else:
                        alert('At end')
                        alerted = True
                elif ord(d) == ord('B') - ord('@'):
                    if x > 0:
                        x -= 1
                        print('\033[D', end='')
                    else:
                        alert('At beginning')
                        alerted = True
                elif ord(d) == ord('O') - ord('@'):
                    leftlines[y : y] = [leftlines[y]]
                    datalines[y : y] = ['']
                    y += 1
                    mark = None
                    x = 0
                    stored = chr(ord('L') - ord('@'))
                elif ord(d) == ord('L') - ord('@'):
                    empty = '\033[0m' + (' ' * self.width + '\n') * len(datalines)
                    print('\033[%i;%iH%s' % (self.top, self.left, empty), end='')
                    for row in range(0, len(leftlines)):
                        leftline = leftlines[row] + ':'
                        if (leftlines[row - 1] == leftlines[row]) and (leftlines[row] == leftlines[-1]):
                            leftline = '>'
                        print('\033[%i;%iH\033[%s34m%s\033[%s39m' % (self.top + row, self.left, '1;' if row == y else '', leftline, '21;' if row == y else ''), end='')
                    for row in range(0, len(datalines)):
                        print('\033[%i;%iH%s\033[49m' % (self.top + row, innerleft, datalines[row]), end='')
                    print('\033[%i;%iH' % (self.top + y, innerleft + x), end='')
                elif d == '\033':
                    d = sys.stdin.read(1)
                    if d == '[':
                        d = sys.stdin.read(1)
                        if d == 'A':
                            stored = chr(ord('P') - ord('@'))
                        elif d == 'B':
                            if y == len(datalines) - 1:
                                alert('At last line')
                                alerted = True
                            else:
                                stored = chr(ord('N') - ord('@'))
                        elif d == 'C':
                            stored = chr(ord('F') - ord('@'))
                        elif d == 'D':
                            stored = chr(ord('B') - ord('@'))
                        elif d == '2':
                            d = sys.stdin.read(1)
                            if d == '~':
                                override = not override
                                status(('modified' if modified else 'unmodified') + (' override' if override else ''))
                        elif d == '3':
                            d = sys.stdin.read(1)
                            if d == '~':
                                removed = 1
                                if (mark is not None) and (mark >= 0) and (mark != x):
                                    if mark < x:
                                        x ^= mark; mark ^= x; x ^= mark
                                    removed = mark - x
                                dataline = datalines[y]
                                if x == len(dataline):
                                    alert('At end')
                                    alerted = True
                                    continue
                                datalines[y] = dataline = dataline[:x] + dataline[x + removed:]
                                print('\033[%i;%iH%s%s\033[%i;%iH' % (self.top + y, innerleft, dataline, ' ' * removed, self.top + y, innerleft + x), end='')
                                mark = None
                                edited = True
                        else:
                            while True:
                                d = sys.stdin.read(1)
                                if (ord('a') <= ord(d)) and (ord(d) <= ord('z')): break
                                if (ord('A') <= ord(d)) and (ord(d) <= ord('Z')): break
                                if d == '~': break
                    elif (d == 'w') or (d == 'W'):
                        if (mark is not None) and (mark >= 0) and (mark != x):
                            selected = datalines[y][mark : x] if mark < x else datalines[y][x : mark]
                            killring.append(selected)
                            mark = None
                            if len(killring) > KILL_MAX:
                                killring = killring[1:]
                        else:
                            alert('No text is selected')
                            alerted = True
                    elif (d == 'y') or (d == 'Y'):
                        if killptr is not None:
                            yanked = killring[killptr]
                            dataline = datalines[y]
                            if (len(yanked) <= x) and (dataline[x - len(yanked) : x] == yanked):
                                killptr -= 1
                                if killptr < 0:
                                    killptr += len(killring)
                                dataline = dataline[:x - len(yanked)] + killring[killptr] + dataline[x:]
                                additional = len(killring[killptr]) - len(yanked)
                                x += additional
                                datalines[y] = dataline
                                print('\033[%i;%iH%s%s\033[%i;%iH' % (self.top + y, innerleft, dataline, ' ' * max(0, -additional), self.top + y, innerleft + x), end='')
                            else:
                                stored = chr(ord('Y') - ord('@'))
                        else:
                            stored = chr(ord('Y') - ord('@'))
                    elif d == 'O':
                        d = sys.stdin.read(1)
                        if d == 'H':
                            x = 0
                        elif d == 'F':
                            x = len(datalines[y])
                        print('\033[%i;%iH' % (self.top + y, innerleft + x), end='')
                elif d == '\n':
                    stored = chr(ord('N') - ord('@'))
            else:
                insert = d
                if len(insert) == 0:
                    continue
                dataline = datalines[y]
                if (not override) or (x == len(dataline)):
                    print(insert + dataline[x:], end='')
                    if len(dataline) - x > 0:
                        print('\033[%iD' % (len(dataline) - x), end='')
                    datalines[y] = dataline[:x] + insert + dataline[x:]
                    if (mark is not None) and (mark >= 0):
                        if mark >= x:
                            mark += len(insert)
                else:
                    print(insert, end='')
                    datalines[y] = dataline[:x] + insert + dataline[x + 1:]
                x += len(insert)
                edited = True



HOME = os.environ['HOME'] if 'HOME' in os.environ else os.path.expanduser('~')
'''
The user's home directory
'''

pipelinein = not sys.stdin.isatty()
'''
Whether stdin is piped
'''

pipelineout = not sys.stdout.isatty()
'''
Whether stdout is piped
'''

pipelineerr = not sys.stderr.isatty()
'''
Whether stderr is piped
'''


usage_program = '\033[34;1mponysay-tool\033[21;39m'

usage = '\n'.join(['%s %s' % (usage_program, '(--help | --version | --kms)'),
                   '%s %s' % (usage_program, '(--edit | --edit-rm) \033[33mPONY-FILE\033[39m'),
                   '%s %s' % (usage_program, '--edit-stash \033[33mPONY-FILE\033[39m > \033[33mSTASH-FILE\033[39m'),
                   '%s %s' % (usage_program, '--edit-apply \033[33mPONY-FILE\033[39m < \033[33mSTASH-FILE\033[39m'),
                   '%s %s' % (usage_program, '(--dimensions | --metadata) \033[33mPONY-DIR\033[39m'),
                   '%s %s' % (usage_program, '--browse \033[33mPONY-DIR\033[39m [-r \033[33mRESTRICTION\033[39m]*'),
               ])

usage = usage.replace('\033[', '\0')
for sym in ('[', ']', '(', ')', '|', '...', '*'):
    usage = usage.replace(sym, '\033[2m' + sym + '\033[22m')
usage = usage.replace('\0', '\033[')

'''
Argument parsing
'''
opts = ArgParser(program     = 'ponysay-tool',
                 description = 'Tool chest for ponysay',
                 usage       = usage,
                 longdescription = None)

opts.add_argumentless(['--no-term-init']) # for debugging

opts.add_argumentless(['-h', '--help'],                          help = 'Print this help message.')
opts.add_argumentless(['+h', '++help', '--help-colour'],         help = 'Print this help message with colours even if piped.')
opts.add_argumentless(['-v', '--version'],                       help = 'Print the version of the program.')
opts.add_argumentless(['--kms'],                                 help = 'Generate all kmsponies for the current TTY palette')
opts.add_argumented(  ['--dimensions'],     arg = 'PONY-DIR',    help = 'Generate pony dimension file for a directory')
opts.add_argumented(  ['--metadata'],       arg = 'PONY-DIR',    help = 'Generate pony metadata collection file for a directory')
opts.add_argumented(  ['-b', '--browse'],   arg = 'PONY-DIR',    help = 'Browse ponies in a directory')
opts.add_argumented(  ['-r', '--restrict'], arg = 'RESTRICTION', help = 'Metadata based restriction for --browse')
opts.add_argumented(  ['--edit'],           arg = 'PONY-FILE',   help = 'Edit a pony file\'s metadata')
opts.add_argumented(  ['--edit-rm'],        arg = 'PONY-FILE',   help = 'Remove metadata from a pony file')
opts.add_argumented(  ['--edit-apply'],     arg = 'PONY-FILE',   help = 'Apply metadata from stdin to a pony file')
opts.add_argumented(  ['--edit-stash'],     arg = 'PONY-FILE',   help = 'Print applyable metadata from a pony file')

unrecognised = not opts.parse()
'''
Whether at least one unrecognised option was used
'''

PonysayTool(args = opts)

