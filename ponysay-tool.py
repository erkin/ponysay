#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
ponysay - Ponysay, cowsay reimplementation for ponies
Copyright (C) 2012  Erkin Batu Altunbaş et al.

This program is free software. It comes without any warranty, to
the extent permitted by applicable law. You can redistribute it
and/or modify it under the terms of the Do What The Fuck You Want
To Public License, Version 2, as published by Sam Hocevar. See
http://sam.zoy.org/wtfpl/COPYING for more details.
'''

import os
import sys
from subprocess import Popen, PIPE

from ponysay import *


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



'''
This is the mane class of ponysay-tool
'''
class PonysayTool():
    '''
    Starts the part of the program the arguments indicate
    
    @param  args:ArgParser  Parsed command line arguments
    '''
    def __init__(self, args):
        if args.argcount == 0:
            args.help()
            exit(255)
            return
        
        opts = args.opts
        
        if unrecognised or (opts['-h'] is not None):
            args.help()
            if unrecognised:
                exit(254)
        
        elif opts['-v'] is not None:
            print('%s %s' % ('ponysay-tool', VERSION))
        
        elif opts['--kms'] is not None:
            self.generateKMS()
        
        elif (opts['--dimensions'] is not None) and (len(opts['--dimensions']) == 1):
            self.generateDimensions(opts['--dimensions'][0])
        
        elif (opts['--edit'] is not None) and (len(opts['--edit']) == 1):
            pony = opts['--edit'][0]
            if not os.path.isfile(pony):
                printerr('%s is not an existing regular file' % pony)
                exit(252)
            linuxvt = ('TERM' in os.environ) and (os.environ['TERM'] == 'linux')
            try:
                print('\033[?1049h', end='') # initialise terminal
                if linuxvt: print('\033[?8c', end='') # use full block for cursor (_ is used by default in linux vt)
                cmd = 'stty %s < %s > /dev/null 2> /dev/null'
                cmd %= ('-echo -icanon -isig -ixoff -ixon', os.path.realpath('/dev/stdout'))
                Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE).wait()
                self.editmeta(pony)
            finally:
                cmd = 'stty %s < %s > /dev/null 2> /dev/null'
                cmd %= ('echo icanon isig ixoff ixon', os.path.realpath('/dev/stdout'))
                Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE).wait()
                if linuxvt: print('\033[?0c', end='') # restore cursor
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
    
    
    '''
    Generate all kmsponies for the current TTY palette
    '''
    def generateKMS(self):
        class PhonyArgParser:
            def __init__(self, key, value):
                self.argcount = 3
                self.message = ponyfile
                self.opts = self
                self.key = key
                self.value = value
            def __getitem__(self, key):
                return [self.value] if key == self.key else None
        
        class StringInputStream:
            def __init__(self):
                self.buf = ''
                class Buffer:
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
            sys.stdout = StringInputStream()
            ponysay = Ponysay()
            ponysay.run(PhonyArgParser('--pony', pony))
        
        for pony in extraponies:
            printerr('Genering extra kmspony: %s' % pony)
            sys.stdout = StringInputStream()
            ponysay = Ponysay()
            ponysay.run(PhonyArgParser('++pony', pony))
        
        sys.stdout = stdout
    
    
    '''
    Generate pony dimension file for a directory
    
    @param  ponydir  The directory
    '''
    def generateDimensions(self, ponydir):
        dimensions = []
        for ponyfile in os.listdir(ponydir):
            if ponyfile.endswith('.pony') and (ponyfile != '.pony'):
                class PhonyArgParser:
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
                stdout = sys.stdout
                class StringInputStream:
                    def __init__(self):
                        self.buf = ''
                        class Buffer:
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
            widths     .append(item[0], item[3])
            heights    .append(item[1], item[3])
            onlyheights.append(item[2], item[3])
        for items in (widths, heights, onlyheights):
            sort(items, key = lambda item : item[0])
        for pair in ((widths, 'widths'), (heights, 'heights'), (onlyheights, 'onlyheights')):
            (items, dimfile) = pair
            dimfile = (ponydir + '/' + dimfile).replace('//'. '/')
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
    
    
    '''
    Edit a pony file's metadata
    
    @param  ponyfile:str  A pony file to edit
    '''
    def editmeta(self, ponyfile):
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
        
        
        class PhonyArgParser:
            def __init__(self):
                self.argcount = 5
                self.message = ponyfile
                self.opts = self
            def __getitem__(self, key):
                if key == '-f':  return [ponyfile]
                if key == '-W':  return ['n']
                return None
        
        
        data = {}
        comment = []
        for line in meta:
            if ': ' in line:
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
        
        cut = 0
        while (len(comment) > cut) and (len(comment[cut]) == 0):
            cut += 1
        comment = comment[cut:]
        
        
        stdout = sys.stdout
        class StringInputStream:
            def __init__(self):
                self.buf = ''
                class Buffer:
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
        
        ## Call `stty` to determine the size of the terminal, this way is better then using python's ncurses
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
        standardfields = ['GROUP NAME', 'NAME', 'OTHER NAMES', 'APPEARANCE', 'KIND',
                          'GROUP', 'BALLOON', 'LINK', 'LINK ON', 'COAT', 'MANE', 'EYE',
                          'AURA', 'DISPLAY', 'BALLOON TOP', 'BALLOON BOTTOM', 'MASTER',
                          'SOURCE', 'MEDIA', 'LICENSE', 'FREE', 'comment']
        for standard in standardfields:
            if standard in fields:
                del fields[fields.index(standard)]
            if standard not in data:
                data[standard] = ''
        
        fields = standardfields[:-1] + fields + [standardfields[-1]]
        
        def saver(ponyfile, ponyheight, ponywidth, data, image):
            class Saver:
                def __init__(self, ponyfile, ponyheight, ponywidth, data, image):
                    (self.ponyfile, self.ponyheight, self.ponywidth, self.data, self.image) = (ponyfile, ponyheight, ponywidth, data, image)
                def __call__(self): # functor
                    comment = self.data['comment']
                    comment = ('\n' + comment + '\n').replace('\n$$$\n', '\n\\$$$\n')[:-1]
                    
                    meta = []
                    for key in self.data:
                        if (key == 'comment') or (len(self.data[key].strip()) == 0):
                            continue
                        values = self.data[key].strip()
                        for value in values.split('\n'):
                            meta.append(key + ': ' + value)
                    
                    meta.append('WIDTH: ' + str(self.ponywidth))
                    meta.append('HEIGHT: ' + str(self.ponyheight))
                    meta.append(comment)
                    meta = '\n'.join(meta)
                    ponydata = '$$$\n' + meta + '\n$$$\n' + '\n'.join(self.image)
                    
                    with open(self.ponyfile, 'wb') as file:
                        file.write(ponydata.encode('utf8'))
                        file.flush()
            return Saver(ponyfile, ponyheight, ponywidth, data, image)
        
        textarea = TextArea(fields, data, 1, 3, termsize[1] - ponywidth, termsize[0] - 2, termsize)
        textarea.run(saver(ponyfile, ponyheight, ponywidth, data, image))



'''
GNU Emacs alike text area
'''
class TextArea:
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
    def __init__(self, fields, datamap, left, top, width, height, termsize):
        (self.fields, self.datamap, self.left, self.top, self.width, self.height, self.termsize) \
        = (fields, datamap, left, top, width - 1, height, termsize)
    
    
    '''
    Execute text reading
    
    @param  saver  Save method
    '''
    def run(self, saver):
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
                            if current is not 'comment':
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



'''
Start the program from ponysay.__init__ if this is the executed file
'''
if __name__ == '__main__':
    '''
    The user's home directory
    '''
    HOME = os.environ['HOME'] if 'HOME' in os.environ else os.path.expanduser('~')
    
    '''
    Whether stdin is piped
    '''
    pipelinein = not sys.stdin.isatty()
    
    '''
    Whether stdout is piped
    '''
    pipelineout = not sys.stdout.isatty()
    
    '''
    Whether stderr is piped
    '''
    pipelineerr = not sys.stderr.isatty()
    
    
    usage_program = '\033[34;1mponysay-tool\033[21;39m'
    
    usage = '\n'.join(['%s %s' % (usage_program, '(--help | --version | --kms)'),
                       '%s %s' % (usage_program, '(--edit | --edit-rm) \033[33mPONY-FILE\033[39m'),
                       '%s %s' % (usage_program, '--edit-stash \033[33mPONY-FILE\033[39m > \033[33mSTASH-FILE\033[39m'),
                       '%s %s' % (usage_program, '--edit-apply \033[33mPONY-FILE\033[39m < \033[33mSTASH-FILE\033[39m'),
                       '%s %s' % (usage_program, '--dimensions \033[33mPONY-DIR\033[39m'),
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
    
    opts.add_argumentless(['-h', '--help'],                         help = 'Print this help message.')
    opts.add_argumentless(['-v', '--version'],                      help = 'Print the version of the program.')
    opts.add_argumentless(['--kms'],                                help = 'Generate all kmsponies for the current TTY palette')
    opts.add_argumented(  ['--dimensions'],     arg = 'PONY-DIR',   help = 'Generate pony dimension file for a directory')
    opts.add_argumented(  ['--edit'],           arg = 'PONY-FILE',  help = 'Edit a pony file\'s metadata')
    opts.add_argumented(  ['--edit-rm'],        arg = 'PONY-FILE',  help = 'Remove metadata from a pony file')
    opts.add_argumented(  ['--edit-apply'],     arg = 'PONY-FILE',  help = 'Apply metadata from stdin to a pony file')
    opts.add_argumented(  ['--edit-stash'],     arg = 'PONY-FILE',  help = 'Print applyable metadata from a pony file')
    
    '''
    Whether at least one unrecognised option was used
    '''
    unrecognised = not opts.parse()
    
    PonysayTool(args = opts)

